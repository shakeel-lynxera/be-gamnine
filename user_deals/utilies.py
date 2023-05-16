from django.core.paginator import Paginator

def custom_pagination(instances, page_number, per_page=10):
    paginator = Paginator(object_list = instances, per_page=per_page)
    page = paginator.get_page(page_number)
    pagination = {
        "total_pages": paginator.num_pages,
        "current_page": page_number,
        "previous_page": 0 if not page.has_previous() else page.previous_page_number(),
        "next_page": 0 if not page.has_next() else page.next_page_number(),
        "has_next": page.has_next(),
        "has_previous": page.has_previous()
    }
    entries = page.object_list
    return entries, pagination