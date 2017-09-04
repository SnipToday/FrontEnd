import os


def mix_panel(request):
    if request.user.is_authenticated:
        user_id = request.user.email
    else:
        user_id = request.session.session_key
    data = {'mixpanel_id': user_id, 'mixpanel_token': os.environ.get('MIXPANEL_TOKEN')}
    return data

