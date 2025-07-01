def extract_name_tag(tags):
    """
    주어진 태그 리스트에서 'Name' 태그의 값을 추출합니다.
    태그가 없거나 'Name'이 없으면 None을 반환합니다.
    """
    if not tags:
        return None
    for tag in tags:
        if tag.get("Key") == "Name":
            return tag.get("Value")
    return None
