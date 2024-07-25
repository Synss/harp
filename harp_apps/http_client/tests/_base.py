from harp.config import ConfigurationBuilder, System, SystemBuilder


class BaseTestDefaultsWith:
    default_applications = ("http_client",)

    async def create_system(self, /, *, applications=None) -> System:
        applications = applications or self.default_applications
        config = ConfigurationBuilder({"applications": applications}, use_default_applications=False)
        return await SystemBuilder(config).abuild()