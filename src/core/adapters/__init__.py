from core.adapters import notification
from core.adapters import slice
from core.adapters import url

from core.adapters.notification import (NotificationController,
                                            NotificationGateway,
                                            notification_controller,
                                            notification_gateway,)
from core.adapters.slice import (SliceController, SliceGateway,
                                     slice_controller, slice_gateway,)
from core.adapters.url import (UrlController, UrlGateway, UrlPresenter,
                                   url_controller, url_gateway, url_presenter,)

__all__ = ['NotificationController', 'NotificationGateway', 'SliceController',
           'SliceGateway', 'UrlController', 'UrlGateway', 'UrlPresenter',
           'notification', 'notification_controller', 'notification_gateway',
           'slice', 'slice_controller', 'slice_gateway', 'url',
           'url_controller', 'url_gateway', 'url_presenter']
