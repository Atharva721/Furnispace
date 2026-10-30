from models import Product

def test_shop_catalog_and_filtering(client, app):
    """Verifies product catalogue listing, category filtering and keyword search."""
    # Catalog
    res = client.get('/shop')
    assert res.status_code == 200
    assert b"Nordic Velvet 3-Seater Sofa" in res.data

    # Filter by category = sofas
    res_sofas = client.get('/shop?category=sofas')
    assert res_sofas.status_code == 200
    assert b"Nordic Velvet 3-Seater Sofa" in res_sofas.data
    # Should not contain bed
    assert b"Kobenhavn Solid Oak Platform Bed" not in res_sofas.data

    # Search keyword
    res_search = client.get('/shop?q=Chesterfield')
    assert res_search.status_code == 200
    assert b"Classic Chesterfield" in res_search.data


def test_product_detail(client):
    """Verifies product detail page displays specs and stock."""
    res = client.get('/product/1')
    assert res.status_code == 200
    assert b"Specifications" in res.data
    assert b"Add to Cart" in res.data


def test_product_comparison_limit(client):
    """Verifies that up to 3 products can be compared, and a 4th is prevented."""
    # Clear compare
    client.get('/compare/clear')

    # Add 1st
    client.get('/compare/add/1', follow_redirects=True)
    # Add 2nd
    client.get('/compare/add/2', follow_redirects=True)
    # Add 3rd
    client.get('/compare/add/3', follow_redirects=True)

    # Verify compare page has 3
    res_compare = client.get('/compare')
    assert res_compare.status_code == 200
    assert b"Compare Products (3/3)" in res_compare.data

    # Attempt to add 4th product
    res_4th = client.get('/compare/add/4', follow_redirects=True)
    assert b"You can compare up to 3 products" in res_4th.data

    # Remove 1st
    client.get('/compare/remove/1', follow_redirects=True)
    res_after_remove = client.get('/compare')
    assert b"Compare Products (2/3)" in res_after_remove.data


def test_advanced_search_and_price_filters(client):
    """Verifies multi-token search, style filter, and price bounds."""
    # 1. Multi-token search: "modern sofa" should match the Nordic velvet sofa
    res_multi = client.get('/shop?q=modern+sofa')
    assert res_multi.status_code == 200
    assert b"Nordic Velvet 3-Seater Sofa" in res_multi.data

    # 2. Plural search: "sofas" should match all sofas
    res_plural = client.get('/shop?q=sofas')
    assert res_plural.status_code == 200
    assert b"Nordic Velvet 3-Seater Sofa" in res_plural.data

    # 3. Style filtering: "Minimalist"
    res_style = client.get('/shop?style=Minimalist')
    assert res_style.status_code == 200
    assert b"Kobenhavn Solid Oak Platform Bed" in res_style.data

    # 4. Price range: max_price=10000
    res_price = client.get('/shop?max_price=10000')
    assert res_price.status_code == 200
    # Higher priced sofa (24999) should not appear
    assert b"Nordic Velvet 3-Seater Sofa" not in res_price.data

