class TenantContext:

    _tenant_id = None

    @staticmethod
    def set_tenant(tenant_id: str):

        TenantContext._tenant_id = tenant_id


    @staticmethod
    def get_tenant():

        return TenantContext._tenant_id