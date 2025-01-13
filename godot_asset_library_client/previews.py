def previews_edit(previews, old_previews, config):
    previews = [
        enhance_preview(p, config)
        for p in previews
    ]
    previews = [
        preview_action(p, old_previews)
        for p in previews
    ] 
    previews += to_remove_previews(previews, old_previews)
    return previews

def enhance_preview(preview, context):
    """
    Enables certain shortcuts for specifying previews.

    >>> class context:
    ...     repo_raw = "https://reporaw.com/path"
    ...
    >>> enhance_preview({'youtube': 'AD8awHLpFxs'}, context)
    {'type': 'video', 'link': 'https://www.youtube.com/watch?v=AD8awHLpFxs', 'thumbnail': 'https://img.youtube.com/vi/AD8awHLpFxs/maxresdefault.jpg'}
    >>> enhance_preview({'repoimage': 'images/myimage.png'}, context)
    {'type': 'image', 'link': 'https://reporaw.com/path/images/myimage.png'}
    >>> enhance_preview({'repothumb': 'thumbs/myimage.jpg'}, context)
    {'thumbnail': 'https://reporaw.com/path/thumbs/myimage.jpg'}
    """
    if 'youtube' in preview:
        youtube_id = preview.pop('youtube')
        preview.update(
            type = "video",
            link = f"https://www.youtube.com/watch?v={youtube_id}",
            thumbnail = f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg",
        )
    if 'repoimage' in preview:
        repoimage = preview.pop('repoimage')
        preview.update(
            type = 'image',
            link = f'{context.repo_raw}/{repoimage}',
        )
    if 'repothumb' in preview:
        repothumb = preview.pop('repothumb')
        preview.update(
            thumbnail = f'{context.repo_raw}/{repothumb}',
        )
    return preview

def preview_action(preview, old_previews):
    """
    Turns a preview in metadata into an action to perform
    (insert, update) with existing previews in the library
    based on matching link field.
    """
    if 'operation' in preview:
        return preview # alredy an op

    for old in old_previews:
        if old['link'] != preview['link']:
            continue
        return dict(
            preview,
            edit_preview_id=old['preview_id'],
            operation='update',
            enabled=True,
        )

    return dict(
        preview,
        operation='insert',
        enabled=True,
    )

def to_remove_previews(previews, old_previews):
    """
    Generates delete edition action to those existing
    previews not defined in the new metadata.
    """
    return [
        dict(
            edit_preview_id=old['preview_id'],
            operation='delete',
            enabled=True,
        )
        for old in old_previews
        if all(
            old['link']!=preview['link']
            for preview in previews
        )
    ]

