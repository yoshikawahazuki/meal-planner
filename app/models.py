from app import db

class Recipe(db.Model): #レシピテーブル
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True) #主キー
    name = db.Column(db.String(100), nullable=False) #レシピ名（必須）
    process = db.Column(db.Text, nullable=True)
    time_category = db.Column(db.String(50)) #朝・昼・夜
    dish_category = db.Column(db.String(50)) #主菜・副菜・汁物

    recipe_ingredients = db.relationship(
        "RecipeIngredient", 
        backref="recipe",
        cascade="all, delete-orphan",#レシピ削除時に紐づく材料も削除する
        passive_deletes=True
    )

class Ingredient(db.Model): #材料テーブル
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True) #主キー
    name = db.Column(db.String(100), nullable=False) #材料(必須）

    recipe_ingredients = db.relationship(
        "RecipeIngredient", 
        backref="ingredient",
        cascade="all, delete-orphan"
        )

class RecipeIngredient(db.Model): #レシピと材料テーブル
    __tablename__ = "recipe_ingredients"

    id = db.Column(db.Integer, primary_key=True) #主キー

    recipe_id = db.Column(
        db.Integer, #int型
        db.ForeignKey("recipes.id"), #レシピID（外部キー）
        nullable=False #必須
    )

    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey("ingredients.id"), #材料ID（外部キー）
        nullable=False
    )

    quantity = db.Column(db.Float, nullable=False) #分量
    unit = db.Column(db.String(20), nullable=False) #単位

class MenuItem(db.Model):
    __tablename__="menu_items"

    id = db.Column(db.Integer, primary_key=True)

    menu_id = db.Column(db.Integer, db.ForeignKey("menus.id"))
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))

    day = db.Column(db.String(10)) #曜日
    timing = db.Column(db.String(10)) #朝・昼・夜

    recipe = db.relationship("Recipe")

class Menu(db.Model):
    __tablename__="menus"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    menu_items = db.relationship(
        "MenuItem",
        backref="menu",
        cascade = "all, delete-orphan"
    )
