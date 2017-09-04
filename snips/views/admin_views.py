from dal_select2.views import Select2QuerySetView
from django.contrib.auth.models import User
from django.db.models import Q


class UserAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_staff:
            return User.objects.none()

        qs = User.objects.all()
        if self.q:
            qs = qs.filter(Q(username__istartswith=self.q) | Q(first_name__istartswith=self.q))
        return qs