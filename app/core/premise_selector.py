class PremiseSelector:
    @staticmethod
    def select_best(premises: list[dict]) -> dict:
        best = {}
        best_score = -9999

        for premise in premises or []:
            score = PremiseSelector.score(premise)

            if score > best_score:
                best_score = score
                best = premise

        if best:
            best["_auto_selected_score"] = best_score

        return best

    @staticmethod
    def score(premise: dict) -> float:
        scores = premise.get("scores", {}) or {}

        hook = PremiseSelector._num(scores.get("hook_strength", 0))
        originality = PremiseSelector._num(scores.get("originality", 0))
        realism = PremiseSelector._num(scores.get("emotional_realism", 0))
        audience = PremiseSelector._num(scores.get("audience_fit", 0))

        risk = str(scores.get("youtube_risk", "medium")).lower()
        penalty = 0

        if risk == "low":
            penalty = 0
        elif "medium" in risk:
            penalty = 1
        elif risk == "high":
            penalty = 3

        return round(
            hook * 0.30
            + originality * 0.30
            + realism * 0.25
            + audience * 0.15
            - penalty,
            2,
        )

    @staticmethod
    def _num(value) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0