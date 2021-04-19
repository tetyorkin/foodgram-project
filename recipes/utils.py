
def get_ingredients_from_js(request):
    ingredients = {}
    for key, ingredient_name in request.POST.items():
        if "nameIngredient" in key:
            _ = key.split("_")
            ingredients[ingredient_name] = int(request.POST[f'valueIngredient_{_[1]}'])
    return ingredients


def get_form_ingredients(request):
    ingredients = {}
    for key, value in request.POST.items():
        if 'nameIngredient' in key:
            ing_id = key.split('_')[-1]
            name = value
            ingredients[ing_id] = [name]
        if 'valueIngredient' in key:
            ing_id = key.split('_')[-1]
            amount = value
            ingredients[ing_id].append(amount)
        if 'unitsIngredient' in key:
            ing_id = key.split('_')[-1]
            units = value
            ingredients[ing_id].append(units)
    return ingredients


def get_tag_create_recipe(request):
    tags_list = []
    for i, j in request.POST.items():
        if j == 'on':
            tags_list.append(i)
    return tags_list
