from krita import DockWidgetFactory, DockWidgetFactoryBase
from .docker_omniverse import DockerOmniverse

DOCKER_ID = 'omniverse_docker'
instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                                        DockWidgetFactoryBase.DockRight,
                                        DockerOmniverse)

instance.addDockWidgetFactory(dock_widget_factory)