from config.ecore import ecore as _ecore
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    ecore = providers.Singleton(_ecore)
