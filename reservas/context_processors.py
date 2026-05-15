from .cart import Carrito


def carrito(request):
    """Expone el conteo del carrito al template base."""
    try:
        c = Carrito(request)
        return {'carrito_count': len(c)}
    except Exception:
        return {'carrito_count': 0}
