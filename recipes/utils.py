
def get_ingredients_from_js(request):
    ingredients = []
    for key in request.POST:
        if key.startswith("nameIngredient"):
            value = key[15:]
            ingredient = []
            ingredient.append(request.POST.get("nameIngredient_" + value))
            ingredient.append(request.POST.get("valueIngredient_" + value))
            ingredient.append(request.POST.get("unitsIngredient_" + value))
            ingredients.append(ingredient)
    return ingredients