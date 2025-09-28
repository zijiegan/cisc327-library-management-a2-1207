"""
Catalog Routes - Book catalog related endpoints
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all_books
from library_service import add_book_to_catalog

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/')
def index():
    """Home page redirects to catalog."""
    return redirect(url_for('catalog.catalog'))

@catalog_bp.route('/catalog')
def catalog():
    """
    Display all books in the catalog.
    Implements R2: Book Catalog Display
    """
    books = get_all_books()
    return render_template('catalog.html', books=books)

@catalog_bp.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Add a new book to the catalog.
    Web interface for R1: Book Catalog Management
    """
    if request.method == 'GET':
        return render_template('add_book.html')
    
    # POST request - process form data
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    isbn = request.form.get('isbn', '').strip()
    
    try:
        total_copies = int(request.form.get('total_copies', ''))
    except (ValueError, TypeError):
        flash('Total copies must be a valid positive integer.', 'error')
        return render_template('add_book.html')
    
    # Use business logic function
    success, message = add_book_to_catalog(title, author, isbn, total_copies)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('catalog.catalog'))
    else:
        flash(message, 'error')
        return render_template('add_book.html')
