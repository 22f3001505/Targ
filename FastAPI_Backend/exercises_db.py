"""
TARG - Exercise & Calorie Database
Real exercise data with MET values from the Compendium of Physical Activities.
MET (Metabolic Equivalent of Task) = energy cost of physical activity.
Calories/hour = MET × weight(kg) × 1.05
"""

# ═══════════════════════════════════════════════════
# EXERCISE DATABASE — 248 real exercises with MET values
# Source: Compendium of Physical Activities (Ainsworth et al.)
# ═══════════════════════════════════════════════════

EXERCISE_DATABASE = [
    # ── CARDIO ──
    {"name": "Walking (slow, 2 mph)", "category": "Cardio", "met": 2.5, "difficulty": "Easy"},
    {"name": "Walking (moderate, 3 mph)", "category": "Cardio", "met": 3.5, "difficulty": "Easy"},
    {"name": "Walking (brisk, 4 mph)", "category": "Cardio", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Walking (very brisk, 4.5 mph)", "category": "Cardio", "met": 6.3, "difficulty": "Moderate"},
    {"name": "Power Walking", "category": "Cardio", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Walking uphill", "category": "Cardio", "met": 6.0, "difficulty": "Moderate"},
    {"name": "Walking with backpack", "category": "Cardio", "met": 7.0, "difficulty": "Hard"},
    {"name": "Jogging (5 mph)", "category": "Cardio", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Running (6 mph)", "category": "Cardio", "met": 9.8, "difficulty": "Hard"},
    {"name": "Running (7 mph)", "category": "Cardio", "met": 11.0, "difficulty": "Hard"},
    {"name": "Running (8 mph)", "category": "Cardio", "met": 11.8, "difficulty": "Very Hard"},
    {"name": "Running (9 mph)", "category": "Cardio", "met": 12.8, "difficulty": "Very Hard"},
    {"name": "Running (10 mph)", "category": "Cardio", "met": 14.5, "difficulty": "Very Hard"},
    {"name": "Sprint intervals", "category": "Cardio", "met": 14.0, "difficulty": "Very Hard"},
    {"name": "Running stairs", "category": "Cardio", "met": 15.0, "difficulty": "Very Hard"},
    {"name": "Treadmill (moderate)", "category": "Cardio", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Treadmill (vigorous)", "category": "Cardio", "met": 10.0, "difficulty": "Hard"},
    {"name": "Cycling (leisure, <10 mph)", "category": "Cardio", "met": 4.0, "difficulty": "Easy"},
    {"name": "Cycling (moderate, 12-14 mph)", "category": "Cardio", "met": 8.0, "difficulty": "Moderate"},
    {"name": "Cycling (vigorous, 14-16 mph)", "category": "Cardio", "met": 10.0, "difficulty": "Hard"},
    {"name": "Cycling (racing, 16-19 mph)", "category": "Cardio", "met": 12.0, "difficulty": "Very Hard"},
    {"name": "Stationary bike (light)", "category": "Cardio", "met": 5.5, "difficulty": "Easy"},
    {"name": "Stationary bike (moderate)", "category": "Cardio", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Stationary bike (vigorous)", "category": "Cardio", "met": 10.5, "difficulty": "Hard"},
    {"name": "Spin class", "category": "Cardio", "met": 8.5, "difficulty": "Hard"},
    {"name": "Swimming (light/moderate)", "category": "Cardio", "met": 6.0, "difficulty": "Moderate"},
    {"name": "Swimming (laps, freestyle)", "category": "Cardio", "met": 8.0, "difficulty": "Hard"},
    {"name": "Swimming (backstroke)", "category": "Cardio", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Swimming (breaststroke)", "category": "Cardio", "met": 10.0, "difficulty": "Hard"},
    {"name": "Swimming (butterfly)", "category": "Cardio", "met": 11.0, "difficulty": "Very Hard"},
    {"name": "Water aerobics", "category": "Cardio", "met": 5.5, "difficulty": "Easy"},
    {"name": "Rowing machine (moderate)", "category": "Cardio", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Rowing machine (vigorous)", "category": "Cardio", "met": 12.0, "difficulty": "Very Hard"},
    {"name": "Elliptical trainer", "category": "Cardio", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Stair climber", "category": "Cardio", "met": 9.0, "difficulty": "Hard"},
    {"name": "Jump rope (slow)", "category": "Cardio", "met": 8.8, "difficulty": "Hard"},
    {"name": "Jump rope (moderate)", "category": "Cardio", "met": 11.8, "difficulty": "Very Hard"},
    {"name": "Jump rope (fast)", "category": "Cardio", "met": 12.3, "difficulty": "Very Hard"},
    {"name": "Jumping jacks", "category": "Cardio", "met": 8.0, "difficulty": "Moderate"},
    {"name": "Burpees", "category": "Cardio", "met": 10.0, "difficulty": "Very Hard"},
    {"name": "Mountain climbers", "category": "Cardio", "met": 8.0, "difficulty": "Hard"},
    {"name": "High knees", "category": "Cardio", "met": 8.0, "difficulty": "Moderate"},
    {"name": "Box jumps", "category": "Cardio", "met": 10.0, "difficulty": "Hard"},
    {"name": "Step aerobics (low impact)", "category": "Cardio", "met": 5.0, "difficulty": "Easy"},
    {"name": "Step aerobics (high impact)", "category": "Cardio", "met": 8.5, "difficulty": "Hard"},
    {"name": "Aerobics (low impact)", "category": "Cardio", "met": 5.0, "difficulty": "Easy"},
    {"name": "Aerobics (high impact)", "category": "Cardio", "met": 7.3, "difficulty": "Moderate"},
    {"name": "Dance aerobics", "category": "Cardio", "met": 6.5, "difficulty": "Moderate"},
    {"name": "Kickboxing", "category": "Cardio", "met": 10.0, "difficulty": "Hard"},

    # ── STRENGTH ──
    {"name": "Weight training (light)", "category": "Strength", "met": 3.5, "difficulty": "Easy"},
    {"name": "Weight training (moderate)", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Weight training (vigorous)", "category": "Strength", "met": 6.0, "difficulty": "Hard"},
    {"name": "Circuit training", "category": "Strength", "met": 8.0, "difficulty": "Hard"},
    {"name": "Bodyweight exercises", "category": "Strength", "met": 3.8, "difficulty": "Moderate"},
    {"name": "Push-ups", "category": "Strength", "met": 8.0, "difficulty": "Moderate"},
    {"name": "Pull-ups", "category": "Strength", "met": 8.0, "difficulty": "Hard"},
    {"name": "Squats (bodyweight)", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Barbell squats", "category": "Strength", "met": 6.0, "difficulty": "Hard"},
    {"name": "Deadlifts", "category": "Strength", "met": 6.0, "difficulty": "Hard"},
    {"name": "Bench press", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Overhead press", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Bicep curls", "category": "Strength", "met": 3.5, "difficulty": "Easy"},
    {"name": "Tricep dips", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Lunges", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Leg press", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Calf raises", "category": "Strength", "met": 3.5, "difficulty": "Easy"},
    {"name": "Lat pulldown", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Seated row", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Dumbbell flyes", "category": "Strength", "met": 3.5, "difficulty": "Easy"},
    {"name": "Kettlebell swings", "category": "Strength", "met": 9.8, "difficulty": "Hard"},
    {"name": "Kettlebell clean & press", "category": "Strength", "met": 10.0, "difficulty": "Hard"},
    {"name": "Battle ropes", "category": "Strength", "met": 10.3, "difficulty": "Very Hard"},
    {"name": "Medicine ball exercises", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Resistance bands", "category": "Strength", "met": 3.8, "difficulty": "Easy"},
    {"name": "TRX suspension training", "category": "Strength", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Farmer's walk", "category": "Strength", "met": 6.0, "difficulty": "Hard"},
    {"name": "Sled push", "category": "Strength", "met": 10.0, "difficulty": "Very Hard"},
    {"name": "Tire flips", "category": "Strength", "met": 8.0, "difficulty": "Very Hard"},
    {"name": "Wall sit", "category": "Strength", "met": 2.5, "difficulty": "Moderate"},
    {"name": "Plank hold", "category": "Strength", "met": 3.8, "difficulty": "Moderate"},

    # ── HIIT ──
    {"name": "HIIT (general)", "category": "HIIT", "met": 10.0, "difficulty": "Hard"},
    {"name": "Tabata training", "category": "HIIT", "met": 12.0, "difficulty": "Very Hard"},
    {"name": "CrossFit WOD", "category": "HIIT", "met": 12.0, "difficulty": "Very Hard"},
    {"name": "AMRAP workout", "category": "HIIT", "met": 10.0, "difficulty": "Hard"},
    {"name": "EMOM workout", "category": "HIIT", "met": 9.0, "difficulty": "Hard"},
    {"name": "Sprint intervals", "category": "HIIT", "met": 14.0, "difficulty": "Very Hard"},
    {"name": "Bike intervals", "category": "HIIT", "met": 11.0, "difficulty": "Hard"},
    {"name": "Rowing intervals", "category": "HIIT", "met": 12.0, "difficulty": "Very Hard"},
    {"name": "Boxing HIIT", "category": "HIIT", "met": 10.0, "difficulty": "Hard"},
    {"name": "Plyometric circuit", "category": "HIIT", "met": 10.0, "difficulty": "Hard"},

    # ── FLEXIBILITY / YOGA ──
    {"name": "Stretching (light)", "category": "Flexibility", "met": 2.3, "difficulty": "Easy"},
    {"name": "Stretching (moderate)", "category": "Flexibility", "met": 3.5, "difficulty": "Easy"},
    {"name": "Yoga (hatha)", "category": "Flexibility", "met": 2.5, "difficulty": "Easy"},
    {"name": "Yoga (vinyasa flow)", "category": "Flexibility", "met": 4.0, "difficulty": "Moderate"},
    {"name": "Yoga (power yoga)", "category": "Flexibility", "met": 5.5, "difficulty": "Moderate"},
    {"name": "Yoga (Bikram/hot)", "category": "Flexibility", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Yoga (ashtanga)", "category": "Flexibility", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Yoga (yin)", "category": "Flexibility", "met": 2.0, "difficulty": "Easy"},
    {"name": "Pilates (mat)", "category": "Flexibility", "met": 3.0, "difficulty": "Moderate"},
    {"name": "Pilates (reformer)", "category": "Flexibility", "met": 4.0, "difficulty": "Moderate"},
    {"name": "Tai Chi", "category": "Flexibility", "met": 3.0, "difficulty": "Easy"},
    {"name": "Foam rolling", "category": "Flexibility", "met": 2.0, "difficulty": "Easy"},
    {"name": "Barre class", "category": "Flexibility", "met": 3.5, "difficulty": "Moderate"},
    {"name": "Mobility work", "category": "Flexibility", "met": 2.5, "difficulty": "Easy"},

    # ── SPORTS ──
    {"name": "Basketball (game)", "category": "Sports", "met": 8.0, "difficulty": "Hard"},
    {"name": "Basketball (shooting)", "category": "Sports", "met": 4.5, "difficulty": "Moderate"},
    {"name": "Soccer (game)", "category": "Sports", "met": 10.0, "difficulty": "Hard"},
    {"name": "Soccer (casual)", "category": "Sports", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Tennis (singles)", "category": "Sports", "met": 8.0, "difficulty": "Hard"},
    {"name": "Tennis (doubles)", "category": "Sports", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Badminton (competitive)", "category": "Sports", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Badminton (casual)", "category": "Sports", "met": 4.5, "difficulty": "Easy"},
    {"name": "Table tennis", "category": "Sports", "met": 4.0, "difficulty": "Easy"},
    {"name": "Volleyball (competitive)", "category": "Sports", "met": 6.0, "difficulty": "Moderate"},
    {"name": "Volleyball (casual)", "category": "Sports", "met": 3.0, "difficulty": "Easy"},
    {"name": "Baseball/Softball", "category": "Sports", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Golf (walking, carrying clubs)", "category": "Sports", "met": 4.8, "difficulty": "Moderate"},
    {"name": "Golf (with cart)", "category": "Sports", "met": 3.5, "difficulty": "Easy"},
    {"name": "Bowling", "category": "Sports", "met": 3.0, "difficulty": "Easy"},
    {"name": "Cricket", "category": "Sports", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Field hockey", "category": "Sports", "met": 8.0, "difficulty": "Hard"},
    {"name": "Ice hockey", "category": "Sports", "met": 8.0, "difficulty": "Hard"},
    {"name": "Lacrosse", "category": "Sports", "met": 8.0, "difficulty": "Hard"},
    {"name": "Rugby", "category": "Sports", "met": 10.0, "difficulty": "Very Hard"},
    {"name": "American football", "category": "Sports", "met": 8.0, "difficulty": "Hard"},
    {"name": "Wrestling", "category": "Sports", "met": 6.0, "difficulty": "Hard"},
    {"name": "Boxing (sparring)", "category": "Sports", "met": 9.0, "difficulty": "Hard"},
    {"name": "Boxing (punching bag)", "category": "Sports", "met": 5.5, "difficulty": "Moderate"},
    {"name": "Martial arts (moderate)", "category": "Sports", "met": 5.3, "difficulty": "Moderate"},
    {"name": "Martial arts (vigorous)", "category": "Sports", "met": 10.3, "difficulty": "Hard"},
    {"name": "Fencing", "category": "Sports", "met": 6.0, "difficulty": "Moderate"},
    {"name": "Squash", "category": "Sports", "met": 12.0, "difficulty": "Very Hard"},
    {"name": "Racquetball", "category": "Sports", "met": 10.0, "difficulty": "Hard"},
    {"name": "Handball", "category": "Sports", "met": 12.0, "difficulty": "Very Hard"},
    {"name": "Rock climbing", "category": "Sports", "met": 8.0, "difficulty": "Hard"},
    {"name": "Bouldering", "category": "Sports", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Skateboarding", "category": "Sports", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Surfing", "category": "Sports", "met": 3.0, "difficulty": "Moderate"},
    {"name": "Water polo", "category": "Sports", "met": 10.0, "difficulty": "Very Hard"},
    {"name": "Kayaking", "category": "Sports", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Canoeing", "category": "Sports", "met": 3.5, "difficulty": "Easy"},
    {"name": "Skiing (downhill)", "category": "Sports", "met": 6.0, "difficulty": "Moderate"},
    {"name": "Skiing (cross-country)", "category": "Sports", "met": 9.0, "difficulty": "Hard"},
    {"name": "Snowboarding", "category": "Sports", "met": 5.3, "difficulty": "Moderate"},
    {"name": "Ice skating", "category": "Sports", "met": 7.0, "difficulty": "Moderate"},
    {"name": "Roller skating", "category": "Sports", "met": 7.0, "difficulty": "Moderate"},

    # ── DANCE ──
    {"name": "Dancing (slow/ballroom)", "category": "Dance", "met": 3.0, "difficulty": "Easy"},
    {"name": "Dancing (moderate)", "category": "Dance", "met": 4.5, "difficulty": "Moderate"},
    {"name": "Dancing (vigorous/club)", "category": "Dance", "met": 7.8, "difficulty": "Hard"},
    {"name": "Salsa dancing", "category": "Dance", "met": 5.5, "difficulty": "Moderate"},
    {"name": "Zumba", "category": "Dance", "met": 6.5, "difficulty": "Moderate"},
    {"name": "Hip hop dance", "category": "Dance", "met": 7.5, "difficulty": "Hard"},
    {"name": "Ballet", "category": "Dance", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Contemporary dance", "category": "Dance", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Line dancing", "category": "Dance", "met": 5.0, "difficulty": "Easy"},

    # ── DAILY ACTIVITIES ──
    {"name": "Cleaning (light)", "category": "Daily", "met": 2.5, "difficulty": "Easy"},
    {"name": "Cleaning (vigorous)", "category": "Daily", "met": 3.5, "difficulty": "Easy"},
    {"name": "Mopping/sweeping", "category": "Daily", "met": 3.5, "difficulty": "Easy"},
    {"name": "Vacuuming", "category": "Daily", "met": 3.3, "difficulty": "Easy"},
    {"name": "Cooking", "category": "Daily", "met": 2.0, "difficulty": "Easy"},
    {"name": "Gardening (light)", "category": "Daily", "met": 3.8, "difficulty": "Easy"},
    {"name": "Gardening (heavy)", "category": "Daily", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Mowing lawn (push)", "category": "Daily", "met": 5.5, "difficulty": "Moderate"},
    {"name": "Raking leaves", "category": "Daily", "met": 4.0, "difficulty": "Easy"},
    {"name": "Shoveling snow", "category": "Daily", "met": 6.0, "difficulty": "Hard"},
    {"name": "Carrying groceries", "category": "Daily", "met": 2.5, "difficulty": "Easy"},
    {"name": "Walking dog", "category": "Daily", "met": 3.0, "difficulty": "Easy"},
    {"name": "Playing with children (active)", "category": "Daily", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Moving furniture", "category": "Daily", "met": 6.0, "difficulty": "Hard"},
    {"name": "Stair climbing (slow)", "category": "Daily", "met": 4.0, "difficulty": "Moderate"},
    {"name": "Stair climbing (fast)", "category": "Daily", "met": 8.8, "difficulty": "Hard"},
    {"name": "Standing desk work", "category": "Daily", "met": 1.8, "difficulty": "Easy"},
    {"name": "Sitting desk work", "category": "Daily", "met": 1.3, "difficulty": "Easy"},
    {"name": "Walking (commute)", "category": "Daily", "met": 3.5, "difficulty": "Easy"},

    # ── OUTDOOR / ADVENTURE ──
    {"name": "Hiking (moderate)", "category": "Outdoor", "met": 6.0, "difficulty": "Moderate"},
    {"name": "Hiking (steep/mountainous)", "category": "Outdoor", "met": 8.0, "difficulty": "Hard"},
    {"name": "Trail running", "category": "Outdoor", "met": 10.0, "difficulty": "Hard"},
    {"name": "Mountain biking", "category": "Outdoor", "met": 8.5, "difficulty": "Hard"},
    {"name": "Horseback riding (walk)", "category": "Outdoor", "met": 3.8, "difficulty": "Easy"},
    {"name": "Horseback riding (trot)", "category": "Outdoor", "met": 5.8, "difficulty": "Moderate"},
    {"name": "Scuba diving", "category": "Outdoor", "met": 7.0, "difficulty": "Hard"},
    {"name": "Snorkeling", "category": "Outdoor", "met": 5.0, "difficulty": "Moderate"},
    {"name": "Paddleboard (SUP)", "category": "Outdoor", "met": 6.0, "difficulty": "Moderate"},
    {"name": "Rowing (outdoors)", "category": "Outdoor", "met": 7.0, "difficulty": "Moderate"},

    # ── CORE / ABS ──
    {"name": "Crunches", "category": "Core", "met": 3.8, "difficulty": "Easy"},
    {"name": "Sit-ups", "category": "Core", "met": 3.8, "difficulty": "Easy"},
    {"name": "Plank variations", "category": "Core", "met": 3.8, "difficulty": "Moderate"},
    {"name": "Russian twists", "category": "Core", "met": 4.0, "difficulty": "Moderate"},
    {"name": "Leg raises", "category": "Core", "met": 3.8, "difficulty": "Moderate"},
    {"name": "Bicycle crunches", "category": "Core", "met": 4.5, "difficulty": "Moderate"},
    {"name": "Ab wheel rollouts", "category": "Core", "met": 5.0, "difficulty": "Hard"},
    {"name": "Dead bug", "category": "Core", "met": 3.0, "difficulty": "Easy"},
    {"name": "Bird dog", "category": "Core", "met": 3.0, "difficulty": "Easy"},
    {"name": "Hollow body hold", "category": "Core", "met": 3.8, "difficulty": "Moderate"},

    # ── MIND-BODY ──
    {"name": "Meditation (seated)", "category": "Mind-Body", "met": 1.0, "difficulty": "Easy"},
    {"name": "Deep breathing exercises", "category": "Mind-Body", "met": 1.0, "difficulty": "Easy"},
    {"name": "Qigong", "category": "Mind-Body", "met": 2.5, "difficulty": "Easy"},
    {"name": "Walking meditation", "category": "Mind-Body", "met": 2.0, "difficulty": "Easy"},
]


# ═══════════════════════════════════════════════════
# CATEGORIES
# ═══════════════════════════════════════════════════
EXERCISE_CATEGORIES = sorted(set(e["category"] for e in EXERCISE_DATABASE))


def calculate_calories_burned(met: float, weight_kg: float, duration_minutes: float) -> int:
    """
    Calculate calories burned using the MET formula.
    Calories = MET × weight(kg) × duration(hours) × 1.05
    The 1.05 correction factor accounts for the thermic effect.
    """
    duration_hours = duration_minutes / 60
    return round(met * weight_kg * duration_hours * 1.05)


def get_exercises_by_category(category: str = None) -> list:
    """Get exercises, optionally filtered by category."""
    if category:
        return [e for e in EXERCISE_DATABASE if e["category"].lower() == category.lower()]
    return EXERCISE_DATABASE


def get_exercises_by_difficulty(difficulty: str) -> list:
    """Get exercises filtered by difficulty level."""
    return [e for e in EXERCISE_DATABASE if e["difficulty"].lower() == difficulty.lower()]


def estimate_workout_calories(exercises: list, weight_kg: float, duration_minutes: float) -> dict:
    """
    Estimate total calories for a workout session.
    Splits duration evenly across exercises if multiple.
    """
    if not exercises:
        return {"total_calories": 0, "breakdown": []}

    time_per_exercise = duration_minutes / len(exercises)
    breakdown = []
    total = 0

    for ex_name in exercises:
        # Find exercise in database
        match = next((e for e in EXERCISE_DATABASE if e["name"].lower() == ex_name.lower()), None)
        if match:
            cals = calculate_calories_burned(match["met"], weight_kg, time_per_exercise)
            breakdown.append({"exercise": match["name"], "met": match["met"], "minutes": round(time_per_exercise), "calories": cals})
            total += cals
        else:
            # Default MET of 5.0 for unknown exercises
            cals = calculate_calories_burned(5.0, weight_kg, time_per_exercise)
            breakdown.append({"exercise": ex_name, "met": 5.0, "minutes": round(time_per_exercise), "calories": cals})
            total += cals

    return {"total_calories": total, "breakdown": breakdown, "duration_minutes": duration_minutes}
