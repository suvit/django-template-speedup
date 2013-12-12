
from django.core.cache import cache
from django.template.loaders.cached import Loader as CachedLoader


class DictToCache(object):
    def __init__(self):
        self.keys = set()

    def __contains__(self, key):
        return cache.get(key) is not None

    def __getitem__(self, key):
        return cache.get(key)

    def __setitem__(self, key, value):
        cache.set(key, value, 60 * 60 * 24 * 30) # one month
        self.keys.add(key)

    def clear(self):
        cache.delete_many(self.keys)
        self.keys.clear()


class DjangoCacheLoader(CachedLoader):
    # django cache loader
    def __init__(self, loaders):
        super(DjangoCacheLoader, self).__init__(loaders)

        # override template_cache_var
        self.template_cache = DictToCache()
