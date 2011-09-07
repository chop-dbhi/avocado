from avocado.models import Report, Scope, Perspective

class SessionReportMiddleware(object):
    def _create_session_objects(self, user):
        # this should only ever occur once per user.
        scope, created = Scope.objects.get_or_create(user=user, session=True)
        perspective, created = Perspective.objects.get_or_create(user=user, session=True)
        report = Report(user=user, scope=scope, perspective=perspective, session=True)
        report.save()
        return report

    def process_request(self, request):
        """Ensures a ``Report`` object is on the session, with associated
        ``Scope`` and ``Perspective`` bound to it.
        """
        user = request.user

        if not user.is_authenticated():
            return

        modified = False

        # fetch this user's session contexts if they exist, otherwise create them
        if not request.session.has_key('report'):
            try:
                report = Report.objects.select_related('scope', 'perspective').get(user=user, session=True)
            except Report.DoesNotExist:
                report = self._create_session_objects(user)

            modified = True
            request.session['report'] = report

        request.session.modified = modified
