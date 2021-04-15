from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template


def get_ingredients_from_js(request):
    ingredients = {}
    for key, ingredient_name in request.POST.items():
        if "nameIngredient" in key:
            _ = key.split("_")
            ingredients[ingredient_name] = int(request.POST[f'valueIngredient_{_[1]}'])
    return ingredients


def get_ingredients(request):
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


def render_to_pdf(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
