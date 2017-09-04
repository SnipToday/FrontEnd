from django.http import Http404, JsonResponse
from django.utils import timezone
from .views_utils import get_anon_views_left
from ..models import Vote, SnipLog, PostMetrics



def update_post_metric(snip_id, action, val=1):
    metric_obj, first_metric = PostMetrics.objects.get_or_create(snip_id=snip_id, defaults={action: 1})
    if not first_metric:
        setattr(metric_obj, action, getattr(metric_obj, action) + val)
        metric_obj.save()


def handle_vote(request, snip_id, vote_type):
    mark_remove = request.POST['param1']
    if mark_remove == Vote.MARK_VOTE:
        vote_obj, created = Vote.objects.get_or_create(user=request.user, snip_id=snip_id, defaults={'vote': vote_type})
        if created:
            update_post_metric(snip_id, vote_type, 1)
        else:
            if vote_obj.vote != vote_type:  # check not receiving the same vote again
                flip_dict = {SnipLog.LIKE: SnipLog.DISLIKE, SnipLog.DISLIKE: SnipLog.LIKE}
                vote_obj.vote = vote_type
                vote_obj.save()
                update_post_metric(snip_id, flip_dict[vote_type], -1)  # decrease by 1 the prev vote
                update_post_metric(snip_id, vote_type, 1)  # increase the current vote
    elif mark_remove == Vote.REMOVE_VOTE:
        num, _ = Vote.objects.filter(user=request.user, snip_id=snip_id).delete()
        update_post_metric(snip_id, vote_type, -1)


def set_action_user_params(request, dict):
    if request.user.is_authenticated():
        dict['user'] = request.user
    else:
        dict['session'] = request.session.session_key


def get_action_additional_params(request):
    param = {}
    try:
        param['param1'] = request.POST['param1']
    except KeyError:
        pass
    try:
        param['param2'] = request.POST['param2']
    except KeyError:
        pass
    return param


def insert_action_to_log(action_dict, params):
    action_obj, is_new_action = SnipLog.objects.get_or_create(**action_dict, defaults=params)
    if not is_new_action:
        for key, value in params.items():
            setattr(action_obj, key, value)
        action_obj.date = timezone.now()
        action_obj.save()
    return is_new_action


def log_view(request, snip_id):
    if request.method != 'POST':
        return JsonResponse({'message': 'Not Post Method'}, status=500)
    try:
        action = request.POST['action']
    except KeyError:
        return JsonResponse({'message': 'Failed to get action'}, status=404)

    VOTES = [SnipLog.LIKE, SnipLog.DISLIKE]

    if action in VOTES:
        if not request.user.is_authenticated():
            return JsonResponse({'message': 'signin'}, status=500)
        try:
            handle_vote(request, snip_id, action)
        except KeyError:
            return JsonResponse({'message': 'missing vote action'}, status=404)

    action_dict = {'snip_id': snip_id, 'action': action}
    set_action_user_params(request, action_dict)
    params = get_action_additional_params(request)
    is_new_action = insert_action_to_log(action_dict, params)
    if is_new_action and action in (SnipLog.READ_MORE, SnipLog.SHARE, SnipLog.VIEWED, SnipLog.OPEN_LINK):
        update_post_metric(snip_id, action, 1)
        # if not request.user.is_authenticated() and action == SnipLog.READ_MORE:
        #     return JsonResponse({'message': 'readmore', 'num_left': get_anon_views_left(request)})

    return JsonResponse({'message': 'success'})
