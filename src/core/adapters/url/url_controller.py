from core.adapters.url.url_gateway import UrlGateway
from core.adapters.url.url_presenter import UrlPresenter
from core.applications.generate_pressigned_url_use_case import GeneratePresignedURLUseCase
from core.dtos.url_dto import UrlRequestDto
from core.interfaces.url import UrlDataSourceInterface
from core.interfaces.url.url_controller_interface import UrlControllerInterface


class UrlController(UrlControllerInterface):

    def __init__(self, datasource: UrlDataSourceInterface):
        self.datasource = datasource

    def generate_presigned_url(self, request: UrlRequestDto) -> dict:
        gateway = UrlGateway(self.datasource)
        use_case = GeneratePresignedURLUseCase(gateway)
        url = use_case.execute(request)
        presenter = UrlPresenter()
        return presenter.return_generate_presigned_url(url)


