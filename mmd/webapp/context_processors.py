from user.models import MyUser

def auth_context(request):
    """Makes session-based id_user and the full user object available in all templates."""
    user_id = request.session.get("id_user")
    current_user = None
    if user_id:
        try:
            current_user = MyUser.objects.get(id=user_id)
        except Exception:
            pass
    return {
        "id_user": user_id,
        "current_user": current_user,
    }
