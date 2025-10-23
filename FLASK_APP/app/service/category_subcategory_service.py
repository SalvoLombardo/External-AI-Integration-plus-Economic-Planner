from app.models import Category, SubCategory
from app.extensions import db

def get_or_create_category(user_id, data):
    # Expect data to have 'category_name' OR 'category_id'
    category_name = data.get('category_name') or data.get('category')
    if not category_name:
        raise ValueError("category_name missing")

    category = Category.query.filter_by(user_id=user_id, name=category_name).first()
    if not category:
        category = Category(
            name=category_name,
            description=data.get('category_description') or data.get('description'),
            user_id=user_id
        )
        db.session.add(category)
        db.session.commit()
    return category.id


def get_or_create_sub_category(category_id, data):
    sub_name = data.get('sub_category_name') or data.get('sub_category') or data.get('name')
    if not sub_name:
        # If you don't want subcategories required, return None or a default
        return None

    sub = SubCategory.query.filter_by(category_id=category_id, name=sub_name).first()
    if not sub:
        sub = SubCategory(
            name=sub_name,
            description=data.get('sub_category_description') or data.get('description'),
            category_id=category_id
        )
        db.session.add(sub)
        db.session.commit()
    return sub.id