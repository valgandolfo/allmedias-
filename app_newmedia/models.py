"""
Models principais do AllMedias PWA
"""
from django.db import models

# Importar models de outros módulos
from .registration.models import UserProfile
from .anota_ai.models import Anotacao, ItemAnotacao

# ===================================================================
# MODELS PRINCIPAIS (serão criados nas próximas implementações)
# ===================================================================

# TODO: Implementar models das funcionalidades principais
# - TBMIDEAS (mídias) -> Já implementado em app_newmedia.medias
# - TBANOTAAI (anotações) -> Já implementado em app_newmedia.anota_ai
# - TBITEM_ANOTAAI (itens de checklist) -> Já implementado em app_newmedia.anota_ai
# - TBTRANSFERENCIA (compartilhamentos)

# Por enquanto, apenas o UserProfile está implementado
__all__ = ['UserProfile', 'Anotacao', 'ItemAnotacao']
