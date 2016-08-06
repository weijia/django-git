from django_git.models import RepoInfo
from iconizer.msg_service.msg_def.file_url_list_msg import TagEnumeratorMsg
from tagging.models import Tag, TaggedItem


def enum_git_repo(tag_name="git"):
    tag_filter = Tag.objects.filter(name=tag_name)
    if tag_filter.exists():
        tag = tag_filter[0]
        tagged_item_list = TaggedItem.objects.filter(tag__exact=tag.pk)
        for tagged_item in tagged_item_list:
            obj_tag = tagged_item.tag.name
            obj = tagged_item.object
            if obj is None:
                continue
            RepoInfo.objects.get_or_create(full_path=obj.full_path)

        for repo in RepoInfo.objects.all().order_by("last_checked"):
            yield repo

