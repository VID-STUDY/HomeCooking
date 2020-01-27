import xlrd
from . import dishservice
from application.core.models import DishCategory


def parse_excel_file(path_to_file: str):
    workbook = xlrd.open_workbook(path_to_file)
    worksheet = workbook.sheet_by_index(0)
    for rx in range(worksheet.nrows):
        if rx == 0:
            continue
        row = worksheet.row(rx)
        product_type = row[1].value
        product_name = row[2].value
        product_dose = row[3].value
        product_form = row[4].value
        units_in_pak = row[6].value
        brand_name = row[7].value
        vendor_name = row[8].value
        product_description = row[10].value
        product_price = row[12].value
        _create_product(product_type, product_name, product_dose,
                        product_form, units_in_pak, brand_name, vendor_name,
                        product_description, product_price)


def _create_product_type(parent_category_name, product_type_name) -> DishCategory:
    parent_category = dishservice.get_category_by_name(parent_category_name, 'ru')

    if not parent_category:
        parent_category = dishservice.create_category('Тип продукта', 'Тип продукта')

    def new_category():
        return dishservice.create_category(product_type_name, product_type_name, parent_category.id)

    product_type_category = parent_category.get_children().filter(DishCategory.name == product_type_name).first()

    if not product_type_category:
        return new_category()
    return product_type_category


def _create_product_type_for_brand(brand_category: DishCategory, product_type_name) -> DishCategory:
    parent_category = brand_category
    product_type_category = parent_category.get_children().filter(DishCategory.name == product_type_name).first()
    if not product_type_category:
        return dishservice.create_category(product_type_name, product_type_name, parent_category.id)
    return product_type_category


def _create_brand_for_product_type(product_type: DishCategory, brand_name) -> DishCategory:
    parent_category = product_type
    brand_category = parent_category.get_children().filter(DishCategory.name == brand_name).first()
    if not brand_category:
        return dishservice.create_category(brand_name, brand_name, parent_category.id)
    return brand_category


def _create_product_type_for_vendor(vendor_category: DishCategory, product_type_name) -> DishCategory:
    parent_category = vendor_category
    product_type_category = parent_category.get_children().filter(DishCategory.name == product_type_name).first()
    if not product_type_category:
        return dishservice.create_category(product_type_name, product_type_name, parent_category.id)
    return product_type_category


def _create_product_brand(brand_name) -> DishCategory:
    parent_category = dishservice.get_category_by_name('Бренд', 'ru')
    if not parent_category:
        parent_category = dishservice.create_category('Бренд', 'Бренд')
    category = dishservice.get_category_by_name(brand_name, 'ru', parent_category=parent_category)
    if category:
        return category
    return dishservice.create_category(brand_name, brand_name, parent_category.id)


def _create_product_vendor(vendor_name) -> DishCategory:
    parent_category = dishservice.get_category_by_name('Производитель', 'ru')
    if not parent_category:
        parent_category = dishservice.create_category('Производитель', 'Производитель')
    category = dishservice.get_category_by_name(vendor_name, 'ru', parent_category=parent_category)
    if category:
        return category
    return dishservice.create_category(vendor_name, vendor_name, parent_category.id)


def _create_product(product_type, product_name, product_dose,
                    product_form, units_in_pak, brand_name,
                    vendor_name, product_description, product_price):
    product_description = _create_description(product_description, product_dose, product_form, units_in_pak)
    if product_price:
        product_price = int(product_price)
    else:
        product_price = 0
    _create_product_for_type(product_type, brand_name, product_name, product_description, product_price)
    _create_product_for_brand(brand_name, product_type, product_name, product_description, product_price)
    _create_product_for_vendor(vendor_name, product_type, product_name, product_description, product_price)


def _create_product_for_type(product_type, brand_name, product_name, product_description, product_price):
    product_type_category = _create_product_type('Тип продукта', product_type)
    category = _create_brand_for_product_type(product_type_category, brand_name)
    dishservice.create_dish(product_name, product_name, product_description,
                            product_description, None, product_price, category.id)


def _create_product_for_brand(product_brand, product_type, product_name, product_description, product_price):
    brand_category = _create_product_brand(product_brand)
    category = _create_product_type_for_brand(brand_category, product_type)
    dishservice.create_dish(product_name, product_name, product_description,
                            product_description, None, product_price, category.id)


def _create_product_for_vendor(product_vendor, product_type, product_name, product_description, product_price):
    vendor_category = _create_product_vendor(product_vendor)
    category = _create_product_type_for_vendor(vendor_category, product_type)
    dishservice.create_dish(product_name, product_name, product_description,
                            product_description, None, product_price, category.id)


def _create_description(product_description: str, product_dose: str, product_form: str, units_in_pak: str) -> str:
    description = product_description
    if product_form:
        description += '\nФорма: {0}'.format(product_form)
    if product_dose:
        description += '\nДоза: {0}'.format(product_dose)
    if units_in_pak:
        description += '\nКоличество в упаковке: {0}'.format(units_in_pak)
    return description
