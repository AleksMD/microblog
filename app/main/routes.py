from flask import render_template, flash, redirect, \
url_for, request, g, jsonify, current_app


from app import db
from app.main.forms import LoginForm, RegistrationForm,\
 EditProfileForm, PostForm,\
 ResetPasswordRequestForm, ResetPasswordForm, SearchForm

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime

from flask_babel import _, get_locale
from guess_language import guess_language
from app.translate import translate
from app.main import bp


@bp.route('/', methods=['POST', 'GET'])
@bp.route('/index', methods=['POST', 'GET'])
@login_required#will not allow access to users that are not authenticated
def index():
	
	form = PostForm()
	
	if form.validate_on_submit():
		language = guess_language(form.post.data)
		print(language)
		
		if language == 'UNKNOWN' or len(language) > 5:
			language = ''
		
		post = Post(body=form.post.data, author=current_user, language=language)
		db.session.add(post)
		db.session.commit()
		flash('Your post is new live!')
		return redirect(url_for('main.index'))
	
	page = request.args.get('page', 1, type=int)
	
	
	posts = current_user.followed_posts().paginate(page,
	 current_app.config['POSTS_PER_PAGE'], False)
	
	next_url = url_for('main.index', page=posts.next_num) \
		if posts.has_next else None
	
	prev_url = url_for('main.index', page=posts.prev_num) \
		if posts.has_prev else None
	
	return render_template('index.html',
	 						title='Homepage', 
	 						form=form, posts=posts.items,
	 						next_url=next_url,
	 						prev_url=prev_url)





@bp.route('/user/<username>')
@login_required#will not allow access to users that are not authenticated
def user(username):
	
	user = User.query.filter_by(username=username).first_or_404()#works like first(), if not results a 404 error to the client
	
	page = request.args.get('page', 1, type=int)
	
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	
	next_url = url_for('main.user', username=user.username, page=posts.next_num) \
		if posts.has_next else None
	
	prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
		if posts.has_prev else None
	
	return render_template('user.html', user=user, posts=posts.items,
							next_url=next_url, prev_url=prev_url)	

@bp.before_request
def before_request():
	#implements local date and time of user last activity
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()	
		g.search_form = SearchForm()
	
	g.locale = str(get_locale())

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required#will not allow access to users that are not authenticated
def edit_profile():
	
	form = EditProfileForm(current_user.username)
	
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('main.edit_profile'))
	
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	
	return render_template('edit_profile.html', title=_('Edit Profile'), form=form)

@bp.route('/follow/<username>')
@login_required#will not allow access to users that are not authenticated
def follow(username):
	
	user = User.query.filter_by(username=username).first()
	
	if user is None:
		flash('User {} not found.'.format(username))
	
	if user == current_user:
		flash('You cannot yourself!')
		return redirect(url_for('main.user', username=username))
	
	current_user.follow(user)
	
	db.session.commit()
	
	flash('You are following {}!'.format(username))
	
	return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required#will not allow access to users that are not authenticated
def unfollow(username):
	
	user = User.query.filter_by(username=username).first()
	
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('main.index'))
	
	if user == current_user:
		flash('You cannot unfollow yourself!')
		return redirect(url_for('main.user', username=username))
	
	current_user.unfollow(user)
	
	db.session.commit()
	
	flash('You are not following {}.'.format(username))
	
	return redirect(url_for('main.user', username=username))

@bp.route('/explore')
@login_required#will not allow access to users that are not authenticated
def explore():
	
	page = request.args.get('page', 1, type=int)
	
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(page,
		current_app.config['POSTS_PER_PAGE'], False)
	
	next_url = url_for('main.explore', page=posts.next_num) \
		if posts.has_next else None
	
	prev_url = url_for('main.explore', page=posts.prev_num) \
		if posts.has_prev else None
	
	return render_template('index.html', 
		title='Explore', posts=posts.items, next_url=next_url, 
		prev_url=prev_url)



@bp.route('/translate', methods=['POST'])
@login_required#will not allow access to users that are not authenticated
def translate_text():
	return jsonify({'text': translate(request.form['text'],
									request.form['source_language'],
									request.form['dest_language'])})

@bp.route('/search')
@login_required#will not allow access to users that are not authenticated
def search():
	
	if not g.search_form.validate():
		return redirect(url_for('main.explore'))
	
	page = request.args.get('page', 1, type=int)
	
	posts, total = Post.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
	
	next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
				if total > page * current_app.config['POSTS_PER_PAGE'] else None
	
	prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
				if page > 1 else None
	
	return render_template('search.html', title=_('Search'), posts=posts, 
							next_url=next_url, prev_url=prev_url)
	