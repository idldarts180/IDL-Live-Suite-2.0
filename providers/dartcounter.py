"""
IDL Live Suite
DartCounter Provider
Version 3.1

Reads live DartCounter match data from the Chrome/Playwright page and
populates the shared Match model used by the broadcast overlay.
"""

import re

from providers.base_provider import BaseProvider
from models.match import Match
from browser.playwright import Browser


class DartCounterProvider(BaseProvider):

    def __init__(self):

        super().__init__()

        self.provider_name = "DartCounter"

        self.match = Match()
        self.match.provider = self.provider_name

        self.browser = Browser(
            profile="browser/dartcounter_profile",
            url="https://app.dartcounter.net/dashboard"
        )

        # DartCounter can be manually scored, so the reliable provider-level
        # signal for a 180 is a submitted visit that reduces the remaining
        # score by exactly 180.
        self._previous_scores = [None, None]

        # Once the two player names have been read successfully, keep them.
        # DartCounter's live page adds/removes visit/history text after each
        # submitted turn, which can shift the body-text layout. Anchoring later
        # reads to the known names makes score tracking stable across turns.
        self._cached_player_names = [None, None]

        # End-of-match tracking. DartCounter leaves the scoring screen
        # immediately after the winning submit.
        self._last_active_player_name = None
        self._last_active_player_index = None
        self._end_screen_handled = False

        # DartCounter can briefly hand the "turn to throw" marker to the other
        # player after the winning submit, just before it navigates to the
        # Rematch/View details screen. If we blindly use that new marker, the
        # wrong player can be announced as the winner.
        #
        # Keep the player who just handed over the turn as a short-lived winner
        # candidate. If that player was sitting on a valid checkout score and
        # the result screen follows immediately, that player made the winning
        # checkout.
        self._update_serial = 0
        self._last_turn_handoff_player_index = None
        self._last_turn_handoff_score = None
        self._last_turn_handoff_serial = None

        # One-shot diagnostic state. After we have definitely seen a live match,
        # dump every DartCounter page the first time the live parser disappears.
        # This tells us exactly what DartCounter renders after the winning dart.
        self._saw_live_match = False
        self._post_match_dumped = False

        # Explicit event consumed by the overlay.
        self.match.match_winner_event = 0
        self.match.match_winner_player = None
        self.match.match_active = False

    # ======================================================
    # Connection
    # ======================================================

    def connect(self):

        self.browser.connect()

        print("Connected to DartCounter.")

    # ======================================================

    def wait_for_match(self):

        print("Waiting for DartCounter match...")

    # ======================================================
    # Helpers
    # ======================================================

    def _get_page(self):
        """
        Return the most relevant DartCounter page.

        Priority:
        1. Completed-match result screen (Rematch / View details)
        2. Live scoring screen
        3. Current/final available page

        This matters because DartCounter can leave a stale live-score page/tab
        available while navigating the active page to the results screen. If we
        choose the stale live page first, the overlay freezes on the pre-finish
        score and never receives the WINNER event.
        """
        try:
            pages = self.browser.context.pages

            # --------------------------------------------------
            # 1. Prefer a genuine completed-match screen.
            # --------------------------------------------------
            for page in reversed(pages):
                try:
                    url = str(page.url).lower()

                    body = page.locator(
                        "body"
                    ).inner_text(timeout=1000)

                    body_upper = body.upper()

                    possible_match_url = (
                        url.endswith("/game/match")
                        or url.endswith("/local-games/match")
                    )

                    has_result_controls = (
                        "REMATCH" in body_upper
                        and "VIEW DETAILS" in body_upper
                    )

                    has_live_scoring = (
                        "TURN TO THROW!" in body_upper
                        or "3-DART AVG." in body_upper
                        or "CHECKOUT RATE" in body_upper
                        or "SUBMIT" in body_upper
                    )

                    if (
                        possible_match_url
                        and has_result_controls
                        and not has_live_scoring
                    ):
                        self.browser.page = page
                        return page

                except Exception:
                    pass

            # --------------------------------------------------
            # 2. Otherwise prefer a visible live match.
            # --------------------------------------------------
            for page in reversed(pages):
                try:
                    body = page.locator(
                        "body"
                    ).inner_text(timeout=1000)

                    if (
                        "3-dart avg." in body
                        and (
                            "BEST OF" in body
                            or "FIRST TO" in body
                            or "RACE TO" in body
                        )
                    ):
                        self.browser.page = page
                        return page

                except Exception:
                    pass

            # --------------------------------------------------
            # 3. Fallbacks.
            # --------------------------------------------------
            if self.browser.page is not None:
                return self.browser.page

            if pages:
                self.browser.page = pages[-1]
                return pages[-1]

        except Exception:
            pass

        return self.browser.page

    # ======================================================

    @staticmethod
    def _clean_lines(text):
        return [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    # ======================================================

    @staticmethod
    def _to_int(value, default=0):
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return default

    # ======================================================

    @staticmethod
    def _to_float(value, default=0.0):
        try:
            cleaned = str(value).strip().replace("%", "")
            return float(cleaned)
        except (TypeError, ValueError):
            return default

    # ======================================================

    def _parse_player_from_average_label(
        self,
        lines,
        avg_index,
        player_index
    ):
        """
        Robust DartCounter player parser.

        DartCounter can insert checkout suggestion text into the player block
        once a player reaches a finish. That means fixed offsets such as
        avg_index - 3 stop being reliable below 170.

        Instead:
        1. Look backwards from the 3-dart-average label.
        2. Find the nearest sensible player-name line.
        3. Read the first numeric value after that name as the remaining score.
        4. Read the following numeric values as sets/legs where applicable.
        """

        window_start = max(0, avg_index - 14)
        block = lines[window_start:avg_index]

        def is_number(value):
            try:
                int(str(value).strip())
                return True
            except (TypeError, ValueError):
                return False

        def is_checkout_token(value):
            value = str(value).strip().upper()

            if value in {"BULL", "DBULL", "BULLSEYE"}:
                return True

            # Dart notation such as T20, D16, S20.
            if re.match(r"^[TDS]\d{1,2}$", value):
                return True

            return False

        blocked_names = {
            "LEGS",
            "SETS",
            "CHECKOUT",
            "CHECKOUT RATE",
            "FIRST 9 AVG.",
            "3-DART AVG.",
            "BEST OF",
            "FIRST TO",
            "RACE TO",
        }

        name_index = None

        cached_name = self._cached_player_names[player_index]

        # After the first successful read, anchor the block to the exact
        # player name. This avoids DartCounter visit/history text being
        # mistaken for the player identity after the first three darts.
        if cached_name:
            for local_index in range(len(block) - 1, -1, -1):
                if block[local_index].strip() == cached_name:
                    name_index = local_index
                    break

        # First read / fallback: discover the nearest sensible name.
        if name_index is None:
            for local_index in range(len(block) - 1, -1, -1):
                candidate = block[local_index].strip()
                upper = candidate.upper()

                if not candidate:
                    continue

                if is_number(candidate):
                    continue

                if is_checkout_token(candidate):
                    continue

                if upper in blocked_names:
                    continue

                if any(
                    upper.startswith(prefix)
                    for prefix in ("BEST OF ", "FIRST TO ", "RACE TO ")
                ):
                    continue

                name_index = local_index
                break

        if name_index is None:
            return None

        name = block[name_index]

        numeric_values = []

        for value in block[name_index + 1:]:
            if is_number(value):
                numeric_values.append(int(value))

        if not numeric_values:
            return None

        # First number after the name is the remaining score.
        score = numeric_values[0]

        if not 0 <= score <= 501:
            return None

        if getattr(self.match, "is_set_play", False):
            sets = numeric_values[1] if len(numeric_values) >= 2 else 0
            legs = numeric_values[2] if len(numeric_values) >= 3 else 0
        else:
            sets = 0
            legs = numeric_values[1] if len(numeric_values) >= 2 else 0

        player = {
            "name": name,
            "score": score,
            "sets": sets,
            "legs": legs,
            "average": 0.0,
            "first9": 0.0,
            "checkout": 0.0,
        }

        if avg_index + 1 < len(lines):
            player["average"] = self._to_float(
                lines[avg_index + 1],
                0.0
            )

        block_end = len(lines)

        for i in range(avg_index + 1, len(lines)):
            if (
                i != avg_index
                and lines[i].lower() == "3-dart avg."
            ):
                block_end = i
                break

        for i in range(avg_index + 1, block_end):
            label = lines[i].lower()

            if label == "first 9 avg." and i + 1 < block_end:
                player["first9"] = self._to_float(
                    lines[i + 1],
                    0.0
                )

            elif label == "checkout rate" and i + 1 < block_end:
                player["checkout"] = self._to_float(
                    lines[i + 1],
                    0.0
                )

        return player

    # ======================================================

    @staticmethod
    def _valid_player_name(value):
        """
        DartCounter briefly reflows parts of its live page after some visits.
        During that transition the old positional parser can momentarily see
        a numeric score/leg value where the player name normally sits.

        Reject those transient frames rather than overwriting the last known
        good player name and score.
        """
        name = str(value).strip()

        if not name:
            return False

        # A genuine player name should not be only a number.
        if name.replace(".", "", 1).isdigit():
            return False

        blocked = {
            "0",
            "1",
            "2",
            "3-DART AVG.",
            "FIRST 9 AVG.",
            "CHECKOUT RATE",
            "LEGS",
            "SETS",
        }

        return name.upper() not in blocked

    def _parse_body_text(self, body_text):

        lines = self._clean_lines(body_text)

        if not lines:
            return False

        # Make sure this really looks like a DartCounter live match.
        if "3-dart avg." not in body_text:
            return False

        # ==========================================
        # Match Format
        # ==========================================

        format_lines = []

        for line in lines[:20]:
            if re.match(
                r"^(BEST OF|FIRST TO|RACE TO)\s+\d+\s+(LEGS?|SETS?)$",
                line,
                flags=re.IGNORECASE
            ):
                format_lines.append(line)

        if format_lines:
            self.match.match_format = " · ".join(format_lines)

        self.match.is_set_play = any(
            "SET" in line.upper()
            for line in format_lines
        )

        # ==========================================
        # Players
        # ==========================================

        average_indexes = [
            index
            for index, line in enumerate(lines)
            if line.lower() == "3-dart avg."
        ]

        players = []

        for player_index, avg_index in enumerate(average_indexes[:2]):
            player = self._parse_player_from_average_label(
                lines,
                avg_index,
                player_index
            )

            if player:
                players.append(player)

        if len(players) < 2:
            return False

        player1 = players[0]
        player2 = players[1]

        # DartCounter can briefly redraw/reorder the score panel when a visit
        # is submitted (especially around large scores such as consecutive
        # 180s). If that transient frame makes a numeric value look like the
        # player name, ignore this refresh completely and keep the last valid
        # Match object. The next 250 ms update will normally contain the
        # settled DOM again.
        if (
            not self._valid_player_name(player1["name"])
            or not self._valid_player_name(player2["name"])
        ):
            return False

        self._cached_player_names[0] = player1["name"]
        self._cached_player_names[1] = player2["name"]

        self.match.player1_name = player1["name"]
        self.match.player1_score = player1["score"]
        self.match.player1_legs = player1["legs"]
        self.match.player1_sets = player1.get("sets", 0)
        self.match.player1_average = player1["average"]
        self.match.player1_first9 = player1["first9"]
        self.match.player1_checkout = player1["checkout"]

        self.match.player2_name = player2["name"]
        self.match.player2_score = player2["score"]
        self.match.player2_legs = player2["legs"]
        self.match.player2_sets = player2.get("sets", 0)
        self.match.player2_average = player2["average"]
        self.match.player2_first9 = player2["first9"]
        self.match.player2_checkout = player2["checkout"]

        self._update_180_events(
            self.match.player1_score,
            self.match.player2_score
        )

        return True

    def _update_180_events(self, player1_score, player2_score):
        """
        Detect submitted 180 visits from score deltas.

        This works for manual DartCounter entry as well as automatic scoring:
        a completed 180 visit changes a player's remaining score by 180.
        """
        current_scores = [player1_score, player2_score]

        for index, current in enumerate(current_scores):
            previous = self._previous_scores[index]

            if previous is not None and previous - current == 180:
                if index == 0:
                    self.match.player1_180_event += 1
                    print("DartCounter: Player 1 hit a 180.")
                else:
                    self.match.player2_180_event += 1
                    print("DartCounter: Player 2 hit a 180.")

            self._previous_scores[index] = current

    @staticmethod
    def _is_checkout_score(score):
        """Return True when a remaining score can be finished in one visit."""
        try:
            score = int(score)
        except (TypeError, ValueError):
            return False

        if score < 2 or score > 170:
            return False

        # Standard impossible three-dart finishes ("bogey numbers").
        return score not in {169, 168, 166, 165, 163, 162, 159}

    @staticmethod
    def _normalise_name(value):
        return " ".join(
            str(value).strip().upper().split()
        )

    def _update_active_player_from_page(self, page):
        """
        Resolve the active DartCounter player from the visible:
            <NAME>'S TURN TO THROW!

        Use the cached player names from the live score parser. This avoids
        fuzzy matching accidentally resolving Player 2 as Player 1.
        """
        try:
            body_text = page.locator("body").inner_text(timeout=1000)

            active_match = re.search(
                r"(?im)^(.+?)['’]S TURN TO THROW!\s*$",
                body_text
            )

            if not active_match:
                return

            active_name = active_match.group(1).strip()
            self._last_active_player_name = active_name

            active = self._normalise_name(active_name)

            # Prefer the parser's cached names because these are the exact
            # names belonging to player slots 0 and 1.
            names = [
                self._normalise_name(
                    self._cached_player_names[0]
                    or getattr(self.match, "player1_name", "")
                ),
                self._normalise_name(
                    self._cached_player_names[1]
                    or getattr(self.match, "player2_name", "")
                ),
            ]

            resolved = None

            # Exact name match first.
            for index, name in enumerate(names):
                if name and active == name:
                    resolved = index
                    break

            # Only use containment if exact matching failed.
            if resolved is None:
                matches = []

                for index, name in enumerate(names):
                    if not name:
                        continue

                    if active in name or name in active:
                        matches.append(index)

                # Use containment only if it identifies exactly one player.
                if len(matches) == 1:
                    resolved = matches[0]

            # DartCounter fallback wording if it ever appears.
            if resolved is None:
                if "OPPONENT" in active:
                    resolved = 1
                elif active in {"YOU", "YOUR", "HOME"}:
                    resolved = 0

            if resolved in (0, 1):
                if resolved != self._last_active_player_index:
                    previous_index = self._last_active_player_index

                    if previous_index in (0, 1):
                        previous_score = (
                            self.match.player1_score
                            if previous_index == 0
                            else self.match.player2_score
                        )

                        self._last_turn_handoff_player_index = previous_index
                        self._last_turn_handoff_score = previous_score
                        self._last_turn_handoff_serial = self._update_serial

                        print(
                            "DartCounter: turn handed over from "
                            f"Player {previous_index + 1} "
                            f"on {previous_score}."
                        )

                    print(
                        "DartCounter: active player -> "
                        f"Player {resolved + 1} ({active_name})"
                    )

                self._last_active_player_index = resolved

        except Exception as exc:
            print(f"DartCounter active-player detection error: {exc}")

    def _winner_index_from_active_name(self):
        """
        Resolve the DartCounter winner across the instant navigation to the
        Rematch/View details screen.

        DartCounter can briefly flip the active-player marker to the opponent
        after the winning dart. When that happens, the player who just handed
        over the turn is the correct winner if they were on a valid checkout
        score immediately beforehand.
        """
        handoff_index = self._last_turn_handoff_player_index
        handoff_score = self._last_turn_handoff_score
        handoff_serial = self._last_turn_handoff_serial

        handoff_is_recent = (
            handoff_index in (0, 1)
            and handoff_serial is not None
            and (self._update_serial - handoff_serial) <= 8
        )

        if (
            handoff_is_recent
            and self._is_checkout_score(handoff_score)
        ):
            print(
                "DartCounter: winner resolved from final turn handoff -> "
                f"Player {handoff_index + 1} "
                f"(checkout score was {handoff_score})."
            )
            return handoff_index

        # Normal case: DartCounter leaves the winning player marked as active
        # until the result screen appears.
        if self._last_active_player_index in (0, 1):
            return self._last_active_player_index

        # Defensive exact-name fallback.
        active = self._normalise_name(
            self._last_active_player_name
        )

        names = [
            self._normalise_name(
                self._cached_player_names[0]
                or getattr(self.match, "player1_name", "")
            ),
            self._normalise_name(
                self._cached_player_names[1]
                or getattr(self.match, "player2_name", "")
            ),
        ]

        for index, name in enumerate(names):
            if active and name and active == name:
                return index

        return None

    def _check_end_of_match_screen(self, page):
        """
        Detect DartCounter's actual completed-match summary screen.

        IMPORTANT:
        The live scoring page can itself use a /game/match or
        /local-games/match URL, so URL alone is NOT enough to identify the
        end of the match. The previous version returned early on that URL and
        stopped player names/scores updating.

        The diagnostic showed the completed-match screen contains:
            Rematch
            View details

        and no longer contains normal live-scoring content.
        """
        try:
            url = str(page.url).lower()

            body_text = page.locator(
                "body"
            ).inner_text(timeout=1000)

            body_upper = body_text.upper()

        except Exception:
            return False

        possible_match_url = (
            url.endswith("/game/match")
            or url.endswith("/local-games/match")
        )

        has_result_controls = (
            "REMATCH" in body_upper
            and "VIEW DETAILS" in body_upper
        )

        # Live scoring commonly contains one or more of these. Their presence
        # means we must continue using the normal score parser.
        has_live_scoring = (
            "TURN TO THROW!" in body_upper
            or "3-DART AVG." in body_upper
            or "CHECKOUT RATE" in body_upper
            or "SUBMIT" in body_upper
        )

        is_end_screen = (
            possible_match_url
            and has_result_controls
            and not has_live_scoring
        )

        if not is_end_screen:
            self._end_screen_handled = False
            return False

        if self._end_screen_handled:
            return True

        winner_index = self._winner_index_from_active_name()

        if winner_index is not None:
            # DartCounter navigates away before a final score=0 live frame is
            # available, so put the winning player into the correct final state.
            if winner_index == 0:
                self.match.player1_score = 0
                self._previous_scores[0] = 0
            else:
                self.match.player2_score = 0
                self._previous_scores[1] = 0

            self.match.match_winner_player = winner_index
            self.match.match_winner_event += 1
            self._end_screen_handled = True

            winner_name = (
                self.match.player1_name
                if winner_index == 0
                else self.match.player2_name
            )

            print(
                "DartCounter: match finished - "
                f"winner detected: {winner_name}"
            )

        return True

    def _dump_pages_after_live_match(self):
        """
        Print a one-shot snapshot of every open DartCounter page after the live
        scoring DOM disappears. This is diagnostic only and is intentionally
        limited to one dump so the terminal stays readable.
        """
        if self._post_match_dumped:
            return

        self._post_match_dumped = True

        print("")
        print("=" * 70)
        print("DARTCOUNTER POST-MATCH DIAGNOSTIC")
        print("=" * 70)

        try:
            pages = list(self.browser.context.pages)
        except Exception as exc:
            print(f"Could not read browser pages: {exc}")
            print("=" * 70)
            return

        print(f"Open pages: {len(pages)}")

        for index, page in enumerate(pages):
            try:
                url = str(page.url)
            except Exception:
                url = "<unable to read url>"

            try:
                title = page.title(timeout=1000)
            except Exception:
                title = "<unable to read title>"

            try:
                body = page.locator("body").inner_text(timeout=1500)
            except Exception as exc:
                body = f"<unable to read body: {exc}>"

            # Keep enough content to identify the result screen without dumping
            # a huge page into the terminal.
            body_preview = body[:4000]

            print("")
            print(f"PAGE {index + 1}")
            print(f"URL: {url}")
            print(f"TITLE: {title}")
            print("--- BODY START ---")
            print(body_preview)
            print("--- BODY END ---")

        print("")
        print("=" * 70)
        print("END DARTCOUNTER POST-MATCH DIAGNOSTIC")
        print("=" * 70)
        print("")

    # ======================================================
    # Live Update
    # ======================================================

    def update(self):

        self._update_serial += 1

        page = self._get_page()

        if page is None:
            return

        # Capture the active thrower continuously. This survives the final
        # navigation even though the live score panel disappears.
        self._update_active_player_from_page(page)

        # Detect DartCounter's dedicated end-of-match page before attempting
        # the normal live-match parser.
        if self._check_end_of_match_screen(page):
            return

        try:
            body_text = page.locator("body").inner_text(
                timeout=3000
            )

            parsed = self._parse_body_text(body_text)

            if parsed:
                # We are definitely back on a live scoring screen. This is
                # important after Rematch/new game because the overlay can now
                # safely release its locked final result.
                was_inactive = not bool(
                    getattr(self.match, "match_active", False)
                )

                self.match.match_active = True
                self.match.match_winner_player = None
                self._end_screen_handled = False
                self._saw_live_match = True
                self._post_match_dumped = False

                if was_inactive:
                    self._last_turn_handoff_player_index = None
                    self._last_turn_handoff_score = None
                    self._last_turn_handoff_serial = None
            else:
                body_upper = body_text.upper()

                # DartCounter's completed local-match screen has now been
                # confirmed by diagnostic output to contain only the normal
                # navigation plus:
                #     Rematch
                #     View details
                #
                # Handle that state directly here. This deliberately does not
                # depend on a separate page-selection/end-screen timing pass:
                # the same body text that failed the live parser is the result
                # screen we need to consume.
                is_completed_match = (
                    self._saw_live_match
                    and "REMATCH" in body_upper
                    and "VIEW DETAILS" in body_upper
                )

                if is_completed_match:
                    self.match.match_active = False

                    if not self._end_screen_handled:
                        winner_index = self._winner_index_from_active_name()

                        print(
                            "DartCounter: completed match detected "
                            "from post-live body."
                        )

                        if winner_index in (0, 1):
                            if winner_index == 0:
                                self.match.player1_score = 0
                                self._previous_scores[0] = 0
                            else:
                                self.match.player2_score = 0
                                self._previous_scores[1] = 0

                            self.match.match_winner_player = winner_index
                            self.match.match_winner_event += 1
                            self._end_screen_handled = True

                            winner_name = (
                                self.match.player1_name
                                if winner_index == 0
                                else self.match.player2_name
                            )

                            print(
                                "DartCounter: match finished - "
                                f"winner detected: {winner_name}"
                            )
                        else:
                            print(
                                "DartCounter: result screen detected but "
                                "winner could not be resolved. "
                                f"last_active_name="
                                f"{self._last_active_player_name!r}, "
                                f"last_active_index="
                                f"{self._last_active_player_index!r}"
                            )

                    return

                print("DartCounter: live match not detected yet.")

                if self._saw_live_match:
                    self._dump_pages_after_live_match()

        except Exception as exc:
            print(f"DartCounter update error: {exc}")

    # ======================================================

    def get_match(self):

        return self.match

    # ======================================================

    def close(self):

        self.browser.close()