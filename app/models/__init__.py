# Importa todos os models para que o SQLAlchemy registre os mappers
from app.models.materia import Materia  # noqa: F401
from app.models.pasta import Pasta  # noqa: F401
from app.models.conteudo import Conteudo  # noqa: F401
from app.models.imagens import Imagem  # noqa: F401
from app.models.audio import Audio  # noqa: F401
from app.models.termos_chave import TermoChave  # noqa: F401
from app.models.videos import VideoYoutube  # noqa: F401
