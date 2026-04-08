from flask import render_template, request, redirect, url_for
from app.models import Recipe
from app.models import Ingredient, RecipeIngredient, Menu, MenuItem
from app import db
from sqlalchemy import and_

def register_routes(app):

    #ホーム画面
    @app.route("/")
    def home():
        return render_template("home.html")

    #レシピ一覧画面
    @app.route("/recipes")
    def show_recipes():
        recipes = Recipe.query.all()

        for recipe in recipes:
            recipe.time_list = recipe.time_category.split(",") if recipe.time_category else []
            recipe.dish_list = recipe.dish_category.split(",") if recipe.dish_category else []

        return render_template("recipes.html", recipes=recipes)
    
    #レシピ詳細画面
    @app.route("/recipes/<int:recipe_id>")
    def show_recipes_detail(recipe_id):
        recipe = Recipe.query.get(recipe_id)

        recipe.time_list = recipe.time_category.split(",") if recipe.time_category else []
        recipe.dish_list = recipe.dish_category.split(",") if recipe.dish_category else []

        return render_template("recipe_detail.html", recipe=recipe)
    
    #レシピ追加画面
    @app.route("/recipes/add", methods=["GET", "POST"])
    def add_recipes():
        if request.method == "POST":
            recipe_name = request.form["recipe_name"]
            ingredient_names = request.form.getlist("ingredient_name")
            quantities = request.form.getlist("quantity")
            units = request.form.getlist("unit")
            process = request.form.get("process")
            times = request.form.getlist("time_category")
            dishes = request.form.getlist("dish_category")

            time_category = ",".join(times)
            dish_category = ",".join(dishes)

            existing = Recipe.query.filter_by(name=recipe_name).first()
            if existing:
                return render_template(
                    "add_recipes.html",
                    error="同じレシピ名は登録できません"
                )

            recipe = Recipe(
                name=recipe_name,
                process=process,
                time_category=time_category,
                dish_category=dish_category
                )
            db.session.add(recipe)
            db.session.commit()

            for name, qty, unit in zip(ingredient_names, quantities, units):
                if not name or not qty or not unit:
                    continue
                ingredient = Ingredient.query.filter_by(name=name).first()
                if not ingredient:
                    ingredient = Ingredient(name=name)
                    db.session.add(ingredient)
                    db.session.flush()

                exists = RecipeIngredient.query.filter_by(
                    recipe_id = recipe.id,
                    ingredient_id = ingredient.id
                ).first()
                if not exists:
                    ri = RecipeIngredient(
                        recipe_id = recipe.id,
                        ingredient_id = ingredient.id,
                        quantity = float(qty),
                        unit = unit
                    )
                    db.session.add(ri)
            db.session.commit()
            return redirect(url_for("show_recipes"))
        return render_template("add_recipes.html")
    
    #レシピ編集
    @app.route("/recipes/<int:recipe_id>/edit", methods=["GET", "POST"])
    def edit_recipe(recipe_id):
        recipe = Recipe.query.get(recipe_id)

        # 既存の時間帯とカテゴリーをリスト化して渡す
        recipe.time_list = recipe.time_category.split(",") if recipe.time_category else []
        recipe.dish_list = recipe.dish_category.split(",") if recipe.dish_category else []

        if request.method == "POST":
            new_name = request.form["recipe_name"]

            existing = Recipe.query.filter_by(name=new_name).first()
            if existing and existing.id != recipe.id:
                return render_template("edit_recipe.html", recipe=recipe, error="同じレシピ名は使えません")

            recipe.name = new_name
            recipe.process = request.form.get("process")

            RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

            ingredient_names = request.form.getlist("ingredient_name")
            quantities = request.form.getlist("quantity")
            units = request.form.getlist("unit")
            times = request.form.getlist("time_category")
            dishes = request.form.getlist("dish_category")

            recipe.time_category = ",".join(times)
            recipe.dish_category = ",".join(dishes)

            for name, qty, unit in zip(ingredient_names, quantities, units):
                if not name or not qty or not unit:
                    continue

                ingredient = Ingredient.query.filter_by(name=name).first()
                if not ingredient:
                    ingredient = Ingredient(name=name)
                    db.session.add(ingredient)
                    db.session.flush()

                ri = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ingredient.id, quantity=float(qty), unit=unit)
                db.session.add(ri)

            db.session.commit()
            return redirect(url_for("show_recipes"))
        return render_template("edit_recipe.html", recipe=recipe)

    #レシピ削除
    @app.route("/recipes/<int:recipe_id>/delete", methods=["POST"])
    def delete_recipe(recipe_id):
        recipe = Recipe.query.get(recipe_id)

        db.session.delete(recipe)
        db.session.commit()

        return redirect(url_for("show_recipes"))

    #献立画面
    @app.route("/menu")
    def show_menu():
        menus = Menu.query.all()
        return render_template("menu.html", menus=menus)
    
    #献立追加画面
    @app.route("/menu/add", methods=["GET", "POST"])
    def add_menu():
        morning_main = Recipe.query.filter(
            and_(Recipe.time_category.like("%朝%"), Recipe.dish_category.like("%主菜%"))
        ).all()
        morning_side = Recipe.query.filter(
            and_(Recipe.time_category.like("%朝%"), Recipe.dish_category.like("%副菜%"))
        ).all()
        morning_soup = Recipe.query.filter(
            and_(Recipe.time_category.like("%朝%"), Recipe.dish_category.like("%汁物%"))
        ).all()

        lunch_main = Recipe.query.filter(
            and_(Recipe.time_category.like("%昼%"), Recipe.dish_category.like("%主菜%"))
        ).all()
        lunch_side = Recipe.query.filter(
            and_(Recipe.time_category.like("%昼%"), Recipe.dish_category.like("%副菜%"))
        ).all()
        lunch_soup = Recipe.query.filter(
            and_(Recipe.time_category.like("%昼%"), Recipe.dish_category.like("%汁物%"))
        ).all()

        dinner_main = Recipe.query.filter(
            and_(Recipe.time_category.like("%夜%"), Recipe.dish_category.like("%主菜%"))
        ).all()
        dinner_side = Recipe.query.filter(
            and_(Recipe.time_category.like("%夜%"), Recipe.dish_category.like("%副菜%"))
        ).all()
        dinner_soup = Recipe.query.filter(
            and_(Recipe.time_category.like("%夜%"), Recipe.dish_category.like("%汁物%"))
        ).all()

        recipe_map = {
            "朝": {"main": morning_main, "side": morning_side, "soup": morning_soup},
            "昼": {"main": lunch_main, "side": lunch_side, "soup": lunch_soup},
            "夜": {"main": dinner_main, "side": dinner_side, "soup": dinner_soup},
        }
        
        menu = Menu.query.first()
        selected_map ={}
        if menu:
            for item in menu.menu_items:
                key = f"{item.day}_{item.timing}"
                if key not in selected_map:
                    selected_map[key] = []
                selected_map[key].append(item.recipe_id)

        if request.method == "POST":
            menu = Menu.query.first()
            if not menu:
                menu = Menu(name="今日の献立")
                db.session.add(menu)
                db.session.flush()
            else:
                MenuItem.query.filter_by(menu_id=menu.id).delete()

            for timing in ["朝", "昼", "夜"]:
                for day in ["月", "火", "水", "木", "金", "土", "日"]:
                    for category in ["main", "side", "soup"]:
                        recipe_ids = request.form.getlist(f"{category}_{day}_{timing}")
                        for recipe_id in recipe_ids:
                            item = MenuItem(
                                menu_id=menu.id,
                                recipe_id=int(recipe_id),
                                day=day,
                                timing=timing
                            )
                            db.session.add(item)

            db.session.commit()
            return redirect(url_for("show_menu"))
        
        return render_template(
            "add_menu.html",
            recipe_map=recipe_map,
            selected_map=selected_map
        )
    
    #買い物リスト画面
    @app.route("/shopping_list")
    def show_shopping_list():
        menu = Menu.query.first()

        ingredient_map = {}

        if menu:
            for item in menu.menu_items:
                recipe = item.recipe

                for ri in recipe.recipe_ingredients:
                    name = ri.ingredient.name
                    qty = ri.quantity
                    unit = ri.unit

                    key = f"{name}_{unit}"

                    if key not in ingredient_map:
                        ingredient_map[key] = {
                            "name": name,
                            "quantity":0,
                            "unit": unit
                        }
                    
                    ingredient_map[key]["quantity"] += qty

        return render_template("shopping_list.html", ingredients=ingredient_map.values())