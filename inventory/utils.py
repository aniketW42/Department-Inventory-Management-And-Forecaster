def is_clerk(user):
    return user.groups.filter(name='Clerk').exists()

def is_faculty(user):
    return user.groups.filter(name='Faculty').exists()

def is_hod(user):
    return user.groups.filter(name='HOD').exists()

