class RoleModel:
    # instance attribute
    def __init__(self, roleID, roleName="", canRole=False,canUser=False, CL111=False, CL222=False, CL333=False):
        self.roleID=roleID
        self.roleName=roleName
        self.canRole = canRole
        self.canUser = canUser
        self.CL111=CL111
        self.CL222=CL222
        self.CL333=CL333