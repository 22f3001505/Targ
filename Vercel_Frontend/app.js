const API_BASE = window.TARG_API_URL || "/api";
const STORAGE_KEY = "targ-vercel-web-state";

const views = [
  ["account", "Account"],
  ["health", "Health"],
  ["recipes", "Recipes"],
  ["workouts", "Workouts"],
  ["macros", "Macros"],
  ["planner", "Planner"],
];

const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const slots = ["breakfast", "lunch", "snack", "dinner"];
const quickMeals = [
  ["Boiled Eggs (2)", 140, 12, 1, 10],
  ["Banana", 105, 1, 27, 0],
  ["Protein Shake", 200, 30, 10, 5],
  ["Chicken Breast (150g)", 250, 46, 0, 5],
  ["Rice (1 cup)", 205, 4, 45, 0],
  ["Mixed Salad", 150, 5, 12, 8],
  ["Paneer (100g)", 265, 18, 1, 20],
  ["Oats + Milk", 310, 13, 50, 7],
];
const starterPlanMeals = [
  "Oats with milk",
  "Grilled chicken salad",
  "Paneer bowl",
  "Rice and vegetables",
  "Protein shake",
  "Fruit and nuts",
  "Egg toast",
  "Lentil soup",
];

const defaultState = {
  token: "",
  user: null,
  health: null,
  recipes: [],
  recipeTitle: "",
  meals: [],
  water: 0,
  workouts: [],
  plan: {},
  goals: null,
};

let route = location.hash.replace("#", "") || "account";
let state = loadState();

const navEl = document.querySelector("#nav");
const viewEl = document.querySelector("#view");
const titleEl = document.querySelector("#pageTitle");
const noticeEl = document.querySelector("#notice");
const accountChip = document.querySelector("#accountChip");

init();

function init() {
  renderNav();
  render();
  checkApi();
  if (state.token) hydrateAccount(false);
  addEventListener("hashchange", () => {
    route = location.hash.replace("#", "") || "account";
    render();
  });
}

function loadState() {
  try {
    return { ...defaultState, ...JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}") };
  } catch {
    return { ...defaultState };
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function setNotice(message, type = "info") {
  if (!message) {
    noticeEl.className = "notice hidden";
    noticeEl.textContent = "";
    return;
  }
  noticeEl.className = `notice ${type}`;
  noticeEl.textContent = message;
}

function renderNav() {
  navEl.innerHTML = views
    .map(([id, label]) => `<button data-route="${id}">${label}<span>${id === route ? "." : ""}</span></button>`)
    .join("");
  navEl.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      location.hash = button.dataset.route;
    });
  });
}

function render() {
  if (!views.some(([id]) => id === route)) route = "account";
  renderNav();
  navEl.querySelectorAll("button").forEach((button) => button.classList.toggle("active", button.dataset.route === route));
  const label = views.find(([id]) => id === route)?.[1] || "Account";
  titleEl.textContent = label;
  accountChip.textContent = state.user ? `@${state.user.username || "user"}` : "Offline";
  renderFlow();
  setNotice("");
  const renderers = {
    account: renderAccount,
    health: renderHealth,
    recipes: renderRecipes,
    workouts: renderWorkouts,
    macros: renderMacros,
    planner: renderPlanner,
  };
  renderers[route]();
}

function renderFlow() {
  const complete = [
    Boolean(state.token),
    Boolean(state.health),
    state.workouts.length > 0,
    state.meals.length > 0 || state.water > 0,
    planCount() > 0,
  ];
  const done = complete.filter(Boolean).length;
  const pct = Math.round((done / complete.length) * 100);
  document.querySelector("#flowTitle").textContent = `${done}/${complete.length} milestones complete`;
  document.querySelector("#flowHint").textContent = nextHint(complete);
  document.querySelector("#flowPercent").textContent = `${pct}%`;
  document.querySelector("#flowFill").style.width = `${pct}%`;
  document.querySelector("#flowBadges").innerHTML = [
    `Sync: ${state.token ? "signed in" : "offline"}`,
    `Health: ${state.health ? "ready" : "needed"}`,
    `Meals: ${state.meals.length}`,
    `Water: ${state.water}`,
    `Workouts: ${state.workouts.length}`,
    `Plan: ${planCount()}`,
  ].map((item) => `<span class="badge">${escapeHtml(item)}</span>`).join("");
}

function nextHint(complete) {
  if (!complete[0]) return "Sign in or create an account to sync progress.";
  if (!complete[1]) return "Run health analysis so recipes, macros, and workouts use your targets.";
  if (!complete[2]) return "Log a workout to complete the fitness step.";
  if (!complete[3]) return "Track a meal or water to build today's dashboard.";
  if (!complete[4]) return "Create a weekly meal plan.";
  return "Core flow is complete. Keep tracking today.";
}

async function checkApi() {
  try {
    const data = await api("/ready");
    document.querySelector("#apiStatus").textContent = "Online";
    document.querySelector("#apiMeta").textContent = `TARG API v${data.version || ""}`;
  } catch {
    document.querySelector("#apiStatus").textContent = "Offline";
    document.querySelector("#apiMeta").textContent = "Using local fallbacks where possible";
  }
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const hasBody = options.body !== undefined;
  if (hasBody && !(options.body instanceof FormData)) headers["Content-Type"] = "application/json";
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof data === "string" ? data : data.detail || data.message || "Request failed";
    if (response.status === 401) logout(false);
    throw new Error(Array.isArray(message) ? message.map((item) => item.msg || item).join(", ") : message);
  }
  return data;
}

function renderAccount() {
  const stats = accountStats();
  viewEl.innerHTML = `
    <div class="grid two">
      <section class="card">
        <h2>Sign in</h2>
        <form id="loginForm" class="grid">
          ${field("loginUser", "Username or email", "text", "", "username@example.com")}
          ${field("loginPass", "Password", "password")}
          <button class="primary-button" type="submit">Sign in</button>
        </form>
      </section>
      <section class="card">
        <h2>Create account</h2>
        <form id="signupForm" class="grid">
          ${field("signupName", "Full name", "text", "", "Your name")}
          ${field("signupEmail", "Email", "email", "", "you@example.com")}
          ${field("signupUser", "Username", "text", "", "username")}
          ${field("signupPass", "Password", "password", "", "At least 8 chars, letter and number")}
          <button class="primary-button" type="submit">Create account</button>
        </form>
      </section>
    </div>
    <section class="card">
      <h2>Account dashboard</h2>
      <div class="metrics">
        ${metric("Saved meals", stats.savedMeals)}
        ${metric("Tracked meals", state.meals.length)}
        ${metric("Workouts", state.workouts.length)}
        ${metric("Plan slots", planCount())}
      </div>
      <div class="actions">
        <button class="secondary-button" id="refreshAccount">Refresh account data</button>
        <button class="danger-button" id="logoutButton">Logout</button>
      </div>
    </section>
  `;
  bindSubmit("loginForm", login);
  bindSubmit("signupForm", signup);
  on("#refreshAccount", () => hydrateAccount(true));
  on("#logoutButton", () => logout(true));
}

async function login(form) {
  const username = value("loginUser");
  const password = value("loginPass");
  const data = await api("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) });
  state.token = data.access_token;
  state.user = data.user;
  saveState();
  await hydrateAccount(false);
  setNotice("Signed in successfully.", "success");
  render();
}

async function signup() {
  const payload = {
    full_name: value("signupName"),
    email: value("signupEmail"),
    username: value("signupUser"),
    password: value("signupPass"),
  };
  const data = await api("/auth/signup", { method: "POST", body: JSON.stringify(payload) });
  state.token = data.access_token;
  state.user = data.user;
  saveState();
  setNotice("Account created. You are signed in.", "success");
  render();
}

function logout(showNotice) {
  state = { ...defaultState };
  saveState();
  if (showNotice) setNotice("Logged out.", "success");
  render();
}

async function hydrateAccount(showNotice) {
  if (!state.token) return;
  try {
    const [profile, meals, water, workouts, plan] = await Promise.allSettled([
      api("/auth/me"),
      api("/user/meals?limit=100"),
      api("/user/water"),
      api("/user/workouts?limit=20"),
      api("/user/meal-plan"),
    ]);
    if (profile.status === "fulfilled") state.user = profile.value;
    if (meals.status === "fulfilled") {
      state.meals = meals.value
        .filter((meal) => meal.meal_type === "tracked")
        .map((meal) => ({
          id: meal.id,
          name: meal.meal_name,
          calories: number(meal.calories),
          protein: number(meal.protein),
          carbs: number(meal.carbs),
          fat: number(meal.fat),
        }));
      state.savedMeals = meals.value.filter((meal) => meal.meal_type === "saved");
    }
    if (water.status === "fulfilled") state.water = number(water.value.glasses);
    if (workouts.status === "fulfilled") state.workouts = workouts.value;
    if (plan.status === "fulfilled" && plan.value.plan_data) state.plan = plan.value.plan_data;
    saveState();
    if (showNotice) setNotice("Account data refreshed.", "success");
    render();
  } catch (error) {
    if (showNotice) setNotice(error.message, "error");
  }
}

function renderHealth() {
  const h = state.health;
  viewEl.innerHTML = `
    <section class="card">
      <h2>Health analysis</h2>
      <form id="healthForm" class="form-grid">
        ${field("age", "Age", "number", 28)}
        ${field("height", "Height (cm)", "number", 175)}
        ${field("weight", "Weight (kg)", "number", 72)}
        <label class="field"><span>Gender</span><select id="gender"><option value="male">Male</option><option value="female">Female</option></select></label>
        <label class="field"><span>Activity level</span><select id="activity"><option value="sedentary">Sedentary</option><option value="light">Light</option><option value="moderate" selected>Moderate</option><option value="active">Active</option><option value="extra_active">Extra active</option></select></label>
        <button class="primary-button" type="submit">Analyze</button>
      </form>
    </section>
    ${h ? renderHealthSummary(h) : `<div class="empty">Run an analysis to unlock diet, workout, and macro targets.</div>`}
  `;
  bindSubmit("healthForm", analyzeHealth);
}

async function analyzeHealth() {
  const payload = {
    age: number(value("age")),
    height: number(value("height")),
    weight: number(value("weight")),
    gender: value("gender"),
    activity_level: value("activity"),
  };
  try {
    state.health = await api("/health/", { method: "POST", body: JSON.stringify(payload) });
  } catch {
    state.health = localHealth(payload);
    setNotice("API unavailable. Local health analysis was used.", "info");
  }
  const cals = state.health.daily_calories?.maintenance || 2000;
  state.goals = {
    calories: cals,
    protein: Math.round((cals * 0.3) / 4),
    carbs: Math.round((cals * 0.45) / 4),
    fat: Math.round((cals * 0.25) / 9),
  };
  saveState();
  render();
}

function renderHealthSummary(h) {
  const c = h.daily_calories || {};
  return `
    <section class="card">
      <h2>Your targets</h2>
      <div class="metrics">
        ${metric("BMI", h.bmi)}
        ${metric("Category", h.bmi_category?.category || "Ready")}
        ${metric("BMR", Math.round(h.bmr || 0))}
        ${metric("Calories", c.maintenance || 0)}
      </div>
    </section>
    <section class="card">
      <h2>Workout preview</h2>
      <p><strong>${escapeHtml(h.workout_plan?.focus || "Balanced Fitness")}</strong></p>
      <ul>${(h.workout_plan?.exercises || []).slice(0, 5).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </section>
  `;
}

function renderRecipes() {
  viewEl.innerHTML = `
    <div class="grid two">
      <section class="card">
        <h2>Nutrition search</h2>
        <form id="nutritionForm" class="form-grid">
          ${field("rCalories", "Calories", "number", mealCalories())}
          ${field("rProtein", "Protein (g)", "number", 30)}
          ${field("rCarbs", "Carbs (g)", "number", 50)}
          ${field("rFat", "Fat (g)", "number", 15)}
          ${field("rFiber", "Fiber (g)", "number", 5)}
          ${field("rResults", "Results", "number", 5)}
          <button class="primary-button" type="submit">Find recipes</button>
        </form>
      </section>
      <section class="card">
        <h2>Ingredient search</h2>
        <form id="ingredientForm" class="grid">
          <label class="field"><span>Ingredients</span><textarea id="ingredients" placeholder="chicken, broccoli, garlic"></textarea></label>
          ${field("iCalories", "Max calories", "number", mealCalories() + 150)}
          ${field("iResults", "Results", "number", 5)}
          <button class="primary-button" type="submit">Search ingredients</button>
        </form>
      </section>
    </div>
    <section class="card">
      <h2>${escapeHtml(state.recipeTitle || "Recipe results")}</h2>
      <div class="result-list" id="recipeResults">${renderRecipeCards(state.recipes)}</div>
    </section>
  `;
  bindSubmit("nutritionForm", nutritionSearch);
  bindSubmit("ingredientForm", ingredientSearch);
  bindRecipeButtons();
}

async function nutritionSearch() {
  const nutrition_input = [
    number(value("rCalories")),
    number(value("rFat")),
    5,
    50,
    500,
    number(value("rCarbs")),
    number(value("rFiber")),
    10,
    number(value("rProtein")),
  ];
  const data = await api("/predict/", {
    method: "POST",
    body: JSON.stringify({ nutrition_input, ingredients: [], params: { n_neighbors: number(value("rResults")), return_distance: false } }),
  });
  state.recipes = data.output || [];
  state.recipeTitle = `Found ${state.recipes.length} matching recipes`;
  saveState();
  render();
}

async function ingredientSearch() {
  const ingredients = value("ingredients").split(",").map((item) => item.trim()).filter(Boolean);
  if (!ingredients.length) throw new Error("Enter at least one ingredient.");
  const data = await api("/predict/", {
    method: "POST",
    body: JSON.stringify({
      nutrition_input: [number(value("iCalories")), 15, 5, 50, 500, 50, 5, 10, 30],
      ingredients,
      params: { n_neighbors: number(value("iResults")), return_distance: false },
    }),
  });
  state.recipes = data.output || [];
  state.recipeTitle = `Found ${state.recipes.length} recipes for ${ingredients.join(", ")}`;
  saveState();
  render();
}

function renderRecipeCards(recipes) {
  if (!recipes.length) return `<div class="empty">Search by nutrition or ingredients to see recommendations.</div>`;
  return recipes.map((recipe, index) => {
    const meal = recipeToMeal(recipe);
    return `
      <article class="recipe-card">
        <h3>${escapeHtml(meal.name)}</h3>
        <div class="macro-line">
          <span>${meal.calories} kcal</span><span>${meal.protein}g protein</span><span>${meal.carbs}g carbs</span><span>${meal.fat}g fat</span>
        </div>
        <div class="actions">
          <button class="secondary-button" data-save-recipe="${index}">Save</button>
          <button class="primary-button" data-track-recipe="${index}">Track</button>
        </div>
      </article>
    `;
  }).join("");
}

function bindRecipeButtons() {
  document.querySelectorAll("[data-save-recipe]").forEach((button) => {
    button.addEventListener("click", () => saveRecipe(number(button.dataset.saveRecipe)));
  });
  document.querySelectorAll("[data-track-recipe]").forEach((button) => {
    button.addEventListener("click", () => {
      addMeal(recipeToMeal(state.recipes[number(button.dataset.trackRecipe)]));
    });
  });
}

async function saveRecipe(index) {
  if (!state.token) throw new Error("Sign in first to save recipes.");
  const meal = recipeToMeal(state.recipes[index]);
  await api("/user/meals", { method: "POST", body: JSON.stringify({ ...meal, meal_name: meal.name, meal_type: "saved" }) });
  setNotice("Recipe saved to account.", "success");
}

function renderWorkouts() {
  const plan = state.health?.workout_plan || {};
  viewEl.innerHTML = `
    <div class="grid two">
      <section class="card">
        <h2>Recommended workout</h2>
        <p><strong>${escapeHtml(plan.focus || "Run health analysis for a personalized plan")}</strong></p>
        <ul>${(plan.exercises || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        <p class="muted">${escapeHtml(plan.tips || "Start steady and build consistency.")}</p>
      </section>
      <section class="card">
        <h2>Calorie calculator</h2>
        <form id="exerciseForm" class="form-grid">
          ${field("exerciseName", "Exercise", "text", "Walking")}
          ${field("exerciseWeight", "Weight (kg)", "number", 72)}
          ${field("exerciseDuration", "Duration (min)", "number", 30)}
          <button class="primary-button" type="submit">Calculate</button>
        </form>
        <div id="exerciseResult" class="empty">Estimate calories before logging.</div>
      </section>
    </div>
    <section class="card">
      <h2>Log workout</h2>
      <form id="workoutForm" class="form-grid">
        ${field("workoutFocus", "Focus", "text", plan.focus || "Balanced Fitness")}
        ${field("workoutDuration", "Duration (min)", "number", 30)}
        ${field("workoutCalories", "Calories burned", "number", 200)}
        ${field("workoutNotes", "Notes", "text", "")}
        <button class="primary-button" type="submit">Log workout</button>
      </form>
    </section>
    <section class="card">
      <h2>Recent workouts</h2>
      <div class="grid">${renderWorkoutRows()}</div>
    </section>
  `;
  bindSubmit("exerciseForm", estimateExercise);
  bindSubmit("workoutForm", logWorkout);
}

async function estimateExercise() {
  const data = await api("/exercises/calories", {
    method: "POST",
    body: JSON.stringify({
      exercise_name: value("exerciseName"),
      weight_kg: number(value("exerciseWeight")),
      duration_minutes: number(value("exerciseDuration")),
    }),
  });
  document.querySelector("#exerciseResult").innerHTML = `<strong>${data.calories_burned} kcal</strong><br><span class="muted">${escapeHtml(data.exercise)} at MET ${data.met}</span>`;
  document.querySelector("#workoutCalories").value = data.calories_burned;
}

async function logWorkout() {
  const workout = {
    workout_focus: value("workoutFocus"),
    exercises_completed: state.health?.workout_plan?.exercises || [value("workoutFocus")],
    duration_minutes: number(value("workoutDuration")),
    calories_burned: number(value("workoutCalories")),
    notes: value("workoutNotes"),
  };
  if (state.token) {
    await api("/user/workouts", { method: "POST", body: JSON.stringify(workout) });
  }
  state.workouts.unshift({ ...workout, logged_at: new Date().toISOString() });
  state.workouts = state.workouts.slice(0, 20);
  saveState();
  setNotice("Workout logged.", "success");
  render();
}

function renderWorkoutRows() {
  if (!state.workouts.length) return `<div class="empty">No workouts logged yet.</div>`;
  return state.workouts.map((item) => `
    <div class="meal-row">
      <div><strong>${escapeHtml(item.workout_focus || "Workout")}</strong><div class="muted">${number(item.duration_minutes)} min, ${number(item.calories_burned)} kcal</div></div>
    </div>
  `).join("");
}

function renderMacros() {
  const goals = state.goals || defaultGoals();
  const totals = mealTotals();
  viewEl.innerHTML = `
    <section class="card">
      <h2>Daily goals</h2>
      <div class="metrics">
        ${metric("Calories", `${totals.calories}/${goals.calories}`)}
        ${metric("Protein", `${totals.protein}/${goals.protein}g`)}
        ${metric("Carbs", `${totals.carbs}/${goals.carbs}g`)}
        ${metric("Fat", `${totals.fat}/${goals.fat}g`)}
      </div>
    </section>
    <div class="grid two">
      <section class="card">
        <h2>Log meal</h2>
        <form id="mealForm" class="form-grid">
          ${field("mealName", "Meal name", "text", "Chicken salad")}
          ${field("mealCalories", "Calories", "number", 400)}
          ${field("mealProtein", "Protein", "number", 30)}
          ${field("mealCarbs", "Carbs", "number", 40)}
          ${field("mealFat", "Fat", "number", 15)}
          <button class="primary-button" type="submit">Add meal</button>
        </form>
        <div class="actions">${quickMeals.map((meal, index) => `<button class="secondary-button" data-quick="${index}">${escapeHtml(meal[0])}</button>`).join("")}</div>
      </section>
      <section class="card">
        <h2>Water</h2>
        <div class="metric"><strong>${state.water}/10</strong><span>glasses today</span></div>
        <div class="water-controls">
          <button class="secondary-button" data-water="-1">-1</button>
          <button class="primary-button" data-water="1">+1</button>
          <button class="primary-button" data-water="2">+2</button>
          <button class="danger-button" data-water-reset>Reset</button>
        </div>
      </section>
    </div>
    <section class="card">
      <h2>Food search</h2>
      <form id="foodSearchForm" class="form-grid">
        ${field("foodQuery", "Food", "text", "", "rice, oats, paneer")}
        <button class="primary-button" type="submit">Search food</button>
      </form>
      <div class="result-list" id="foodResults"></div>
    </section>
    <section class="card">
      <h2>Today's meals</h2>
      <div class="grid">${renderMealRows()}</div>
      <div class="actions"><button class="danger-button" id="clearMeals">Clear meals</button></div>
    </section>
  `;
  bindSubmit("mealForm", () => addMeal({
    name: value("mealName"),
    calories: number(value("mealCalories")),
    protein: number(value("mealProtein")),
    carbs: number(value("mealCarbs")),
    fat: number(value("mealFat")),
  }));
  bindSubmit("foodSearchForm", searchFood);
  document.querySelectorAll("[data-quick]").forEach((button) => button.addEventListener("click", () => {
    const [name, calories, protein, carbs, fat] = quickMeals[number(button.dataset.quick)];
    addMeal({ name, calories, protein, carbs, fat });
  }));
  document.querySelectorAll("[data-water]").forEach((button) => button.addEventListener("click", () => updateWater(state.water + number(button.dataset.water))));
  on("[data-water-reset]", () => updateWater(0));
  on("#clearMeals", clearMeals);
}

async function addMeal(meal) {
  const normalized = {
    name: meal.name || meal.meal_name || "Meal",
    calories: number(meal.calories),
    protein: number(meal.protein),
    carbs: number(meal.carbs),
    fat: number(meal.fat),
  };
  if (state.token) {
    try {
      const saved = await api("/user/meals", { method: "POST", body: JSON.stringify({ ...normalized, meal_name: normalized.name, meal_type: "tracked" }) });
      normalized.id = saved.meal_id;
    } catch {
      setNotice("Backend unavailable. Meal tracked locally for this browser.", "info");
    }
  }
  state.meals.push(normalized);
  saveState();
  setNotice("Meal added to tracker.", "success");
  render();
}

async function clearMeals() {
  if (state.token) {
    try {
      await api("/user/meals/clear", { method: "DELETE" });
    } catch {
      setNotice("Could not clear cloud meals. Local list was reset.", "info");
    }
  }
  state.meals = [];
  saveState();
  render();
}

async function updateWater(glasses) {
  state.water = Math.max(0, Math.min(40, glasses));
  if (state.token) {
    try {
      const data = await api("/user/water", { method: "PUT", body: JSON.stringify({ glasses: state.water }) });
      state.water = number(data.glasses);
    } catch {
      setNotice("Water saved locally because sync is unavailable.", "info");
    }
  }
  saveState();
  render();
}

async function searchFood() {
  const q = value("foodQuery");
  const data = await api(`/foods/search?q=${encodeURIComponent(q)}&limit=12`);
  const foods = data.foods || [];
  document.querySelector("#foodResults").innerHTML = foods.length ? foods.map((food, index) => `
    <article class="recipe-card">
      <h3>${escapeHtml(food.name)}</h3>
      <div class="macro-line"><span>${number(food.calories)} kcal</span><span>${number(food.protein)}g protein</span><span>${number(food.carbs)}g carbs</span><span>${number(food.fat)}g fat</span></div>
      <button class="primary-button" data-add-food="${index}">Add to log</button>
    </article>
  `).join("") : `<div class="empty">No foods found.</div>`;
  document.querySelectorAll("[data-add-food]").forEach((button) => button.addEventListener("click", () => addMeal(foods[number(button.dataset.addFood)])));
}

function renderMealRows() {
  if (!state.meals.length) return `<div class="empty">No meals logged yet.</div>`;
  return state.meals.map((meal, index) => `
    <div class="meal-row">
      <div>
        <strong>${escapeHtml(meal.name)}</strong>
        <div class="macro-line"><span>${number(meal.calories)} kcal</span><span>${number(meal.protein)}g protein</span><span>${number(meal.carbs)}g carbs</span><span>${number(meal.fat)}g fat</span></div>
      </div>
      <button class="ghost-button" data-delete-meal="${index}">x</button>
    </div>
  `).join("");
}

function renderPlanner() {
  const plan = normalizedPlan();
  viewEl.innerHTML = `
    <section class="card">
      <h2>Weekly meal planner</h2>
      <div class="actions">
        <button class="secondary-button" id="randomizePlan">Randomize week</button>
        <button class="primary-button" id="savePlan">Save plan</button>
        <button class="secondary-button" id="loadPlan">Load saved plan</button>
      </div>
    </section>
    <section class="grid">
      ${days.map((day) => `
        <article class="day-card">
          <h3>${day}</h3>
          <div class="form-grid">
            ${slots.map((slot) => field(`${day}_${slot}`, title(slot), "text", plan[day]?.[slot] || "")).join("")}
          </div>
        </article>
      `).join("")}
    </section>
    <section class="card">
      <h2>Grocery list</h2>
      <div class="empty">${groceryList(plan).map(escapeHtml).join("<br>") || "Add meals to build a grocery list."}</div>
    </section>
  `;
  days.forEach((day) => slots.forEach((slot) => {
    const input = document.getElementById(`${day}_${slot}`);
    input.addEventListener("input", () => {
      state.plan = normalizedPlan();
      state.plan[day][slot] = input.value;
      saveState();
      renderFlow();
    });
  }));
  on("#randomizePlan", randomizePlan);
  on("#savePlan", savePlan);
  on("#loadPlan", () => hydrateAccount(true));
}

function randomizePlan() {
  const pool = state.savedMeals?.map((meal) => meal.meal_name) || [];
  const source = pool.length ? pool : starterPlanMeals;
  const next = {};
  days.forEach((day, dayIndex) => {
    next[day] = {};
    slots.forEach((slot, slotIndex) => {
      next[day][slot] = source[(dayIndex * slots.length + slotIndex) % source.length];
    });
  });
  state.plan = next;
  saveState();
  render();
}

async function savePlan() {
  if (!state.token) throw new Error("Sign in first to save a plan.");
  const payload = { plan_data: normalizedPlan(), week_start: new Date().toISOString().slice(0, 10) };
  await api("/user/meal-plan", { method: "POST", body: JSON.stringify(payload) });
  setNotice("Meal plan saved.", "success");
}

function normalizedPlan() {
  const plan = {};
  days.forEach((day) => {
    plan[day] = {};
    slots.forEach((slot) => {
      plan[day][slot] = state.plan?.[day]?.[slot] || "";
    });
  });
  return plan;
}

function groceryList(plan) {
  const items = new Set();
  Object.values(plan).forEach((day) => Object.values(day).forEach((meal) => {
    String(meal || "").split(/,|\+|and/i).map((item) => item.trim()).filter(Boolean).forEach((item) => items.add(item));
  }));
  return [...items].sort();
}

function bindSubmit(id, handler) {
  document.getElementById(id)?.addEventListener("submit", async (event) => {
    event.preventDefault();
    setNotice("");
    try {
      await handler(new FormData(event.currentTarget));
    } catch (error) {
      setNotice(error.message || "Action failed.", "error");
    }
  });
}

function on(selector, handler) {
  document.querySelector(selector)?.addEventListener("click", async (event) => {
    event.preventDefault();
    setNotice("");
    try {
      await handler(event);
    } catch (error) {
      setNotice(error.message || "Action failed.", "error");
    }
  });
}

function field(id, label, type = "text", valueText = "", placeholder = "") {
  return `
    <label class="field">
      <span>${escapeHtml(label)}</span>
      <input id="${id}" type="${type}" value="${escapeHtml(valueText)}" placeholder="${escapeHtml(placeholder)}" />
    </label>
  `;
}

function metric(label, valueText) {
  return `<div class="metric"><strong>${escapeHtml(valueText)}</strong><span>${escapeHtml(label)}</span></div>`;
}

function value(id) {
  return document.getElementById(id)?.value?.trim() || "";
}

function number(input) {
  const n = Number(input);
  return Number.isFinite(n) ? Math.round(n * 10) / 10 : 0;
}

function title(text) {
  return text.slice(0, 1).toUpperCase() + text.slice(1);
}

function escapeHtml(valueText) {
  return String(valueText ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function mealCalories() {
  return Math.min(1000, Math.max(200, Math.round(((state.health?.daily_calories?.maintenance || 1500) / 3) / 10) * 10));
}

function recipeToMeal(recipe) {
  return {
    name: recipe?.Name || recipe?.name || "Recipe",
    calories: number(recipe?.Calories ?? recipe?.calories),
    protein: number(recipe?.ProteinContent ?? recipe?.protein),
    carbs: number(recipe?.CarbohydrateContent ?? recipe?.carbs),
    fat: number(recipe?.FatContent ?? recipe?.fat),
  };
}

function defaultGoals() {
  const cals = state.health?.daily_calories?.maintenance || 2000;
  return {
    calories: cals,
    protein: Math.round((cals * 0.3) / 4),
    carbs: Math.round((cals * 0.45) / 4),
    fat: Math.round((cals * 0.25) / 9),
  };
}

function mealTotals() {
  return state.meals.reduce((totals, meal) => ({
    calories: totals.calories + number(meal.calories),
    protein: totals.protein + number(meal.protein),
    carbs: totals.carbs + number(meal.carbs),
    fat: totals.fat + number(meal.fat),
  }), { calories: 0, protein: 0, carbs: 0, fat: 0 });
}

function planCount() {
  return Object.values(state.plan || {}).reduce((count, day) => count + Object.values(day || {}).filter(Boolean).length, 0);
}

function accountStats() {
  return {
    savedMeals: state.savedMeals?.length || 0,
  };
}

function localHealth(input) {
  const heightM = input.height / 100;
  const bmi = number(input.weight / (heightM * heightM));
  const category = bmi < 18.5 ? "Underweight" : bmi < 25 ? "Normal" : bmi < 30 ? "Overweight" : "Obese";
  const bmr = input.gender === "male"
    ? 10 * input.weight + 6.25 * input.height - 5 * input.age + 5
    : 10 * input.weight + 6.25 * input.height - 5 * input.age - 161;
  const multipliers = { sedentary: 1.2, light: 1.375, moderate: 1.55, active: 1.725, extra_active: 1.9 };
  const maintenance = Math.round(bmr * (multipliers[input.activity_level] || 1.55));
  return {
    bmi,
    bmi_category: { category, status: "Local estimate" },
    bmr: number(bmr),
    daily_calories: {
      maintenance,
      mild_loss: Math.round(maintenance * 0.9),
      weight_loss: Math.round(maintenance * 0.8),
      weight_gain: Math.round(maintenance * 1.2),
    },
    workout_plan: {
      focus: category === "Normal" ? "Balanced Fitness" : category === "Underweight" ? "Strength Building" : "Low-impact fat loss",
      exercises: ["Brisk walking", "Strength training", "Mobility work", "Core training"],
      tips: "Keep sessions consistent and progress gradually.",
    },
  };
}

document.addEventListener("click", async (event) => {
  const deleteButton = event.target.closest("[data-delete-meal]");
  if (!deleteButton) return;
  const index = number(deleteButton.dataset.deleteMeal);
  const meal = state.meals[index];
  if (state.token && meal?.id) {
    try {
      await api(`/user/meals/${meal.id}`, { method: "DELETE" });
    } catch {
      setNotice("Could not delete from cloud. Removed locally.", "info");
    }
  }
  state.meals.splice(index, 1);
  saveState();
  render();
});
