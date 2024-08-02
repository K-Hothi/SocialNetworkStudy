from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, jsonify
from flask_login import login_required, current_user
from .models import Class, User, Notes, Qcards, Tests, Following,likesNotes, likesTests, likesCards, Reviews, Message, FollowingUser, Question, Answer
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, func, desc
from . import db
import os
from datetime import datetime

views = Blueprint('views', __name__)

WebsiteName = "The Study Resource"

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
        # Get the IDs of classes the user is following
    following_ids = [following.class_id for following in Following.query.filter_by(user_id=current_user.id).all()]

    # Filter classes based on the user's following relationships
    followedClasses = Class.query.filter(Class.id.in_(following_ids)).all()
    if request.method == 'POST':
        className = request.form.get('class')
        name = request.form.get('title')
        class_id=Class.query.filter_by(name=className).first()
        files = request.files['files']
        fileType = request.form.get('fileType')

        if fileType == "notes":
            counter = 1
            new_filename = files.filename
            while Notes.query.filter_by(fileName=new_filename).first():
                basename, extension = os.path.splitext(files.filename)
                new_filename = f"{basename}_{counter}{extension}"
                counter += 1

        elif fileType == "q-cards":
            counter = 1
            new_filename = files.filename
            while Qcards.query.filter_by(fileName=new_filename).first():
                basename, extension = os.path.splitext(files.filename)
                new_filename = f"{basename}_{counter}{extension}"
                counter += 1

        elif fileType == "practice-test":
            counter = 1
            new_filename = files.filename
            while Tests.query.filter_by(fileName=new_filename).first():
                basename, extension = os.path.splitext(files.filename)
                new_filename = f"{basename}_{counter}{extension}"
                counter += 1

        else:
            counter = 1
            new_filename = files.filename
            while Notes.query.filter_by(fileName=new_filename).first():
                basename, extension = os.path.splitext(files.filename)
                new_filename = f"{basename}_{counter}{extension}"
                counter += 1



        files.filename = new_filename.replace(" ", "_")


        if fileType == "notes":
            newNote = Notes(name=name.title(), fileName=files.filename,  user_id=current_user.id, class_id=class_id.id, likesCountNotes=0)
        elif fileType =="q-cards":
            newNote = Qcards(name=name.title(), fileName=files.filename,  user_id=current_user.id, class_id=class_id.id, likesCountCards=0)
        elif fileType =="practice-test":
            newNote = Tests(name=name.title(), fileName=files.filename,  user_id=current_user.id, class_id=class_id.id, likesCountTests=0)
        else:
            newNote = Notes(name=name.title(), fileName=files.filename,  user_id=current_user.id, class_id=class_id.id, likesCountNotes=0)

        files.save(files.filename)
        db.session().add(newNote)
        db.session.commit()
        flash("Note Added", category='success')

    following_friends_id = [following.user_id_followed for following in FollowingUser.query.filter_by(user_id=current_user.id).all()]
    followedFriends = User.query.filter(User.id.in_(following_friends_id)).all()

    followers_count_friends = FollowingUser.query.filter_by(user_id_followed=current_user.id).count()

    return render_template("home.html", user=current_user, classes=Class.query.order_by(Class.name).all(), classesPopular=reversed(Class.query.order_by(Class.following_count).all()), classesForward=Class.query.order_by(Class.name).all(), Forwardnotess=Notes.query.all(), followedClassesMain=followedClasses, WebsiteName=WebsiteName, followedFriends=followedFriends, followers_count_friends=followers_count_friends)

@views.route('/addClass', methods=['GET', 'POST'])
@login_required
def addClass():
    if request.method == 'POST':
        name = request.form.get('title')
        description = request.form.get('description')
        names = Class.query.filter_by(name=name.title()).first()

        if names:
            flash(f'class already exists', category='error')
        else:
            new_class = Class(name=name.title(), user_id=current_user.id,description=description, following_count=0)
            db.session().add(new_class)
            db.session.commit()
            flash("Class Added", category='success')

    return render_template('addClass.html')

@views.route('/seeMore', methods=['GET', 'POST'])
@login_required
def seeMore():
    following_ids = [following.class_id for following in Following.query.filter_by(user_id=current_user.id).all()]
    followedClasses = Class.query.filter(Class.id.in_(following_ids)).all()

    user_likes_notes = [likes.note_id for likes in likesNotes.query.filter_by(user_id=current_user.id).all()]
    user_likes_cards = [likes.card_id for likes in likesCards.query.filter_by(user_id=current_user.id).all()]
    user_likes_tests = [likes.test_id for likes in likesTests.query.filter_by(user_id=current_user.id).all()]


    if request.method == 'POST':
        class_name = request.form.get('classn')
        main_class = Class.query.filter_by(name=class_name).first()
        sum = Notes.query.filter_by(class_id=main_class.id).count() + Tests.query.filter_by(class_id=main_class.id).count() + Qcards.query.filter_by(class_id=main_class.id).count()
        followers = Following.query.filter_by(class_id=main_class.id).all()
        folower_objects_count = [follower.user_id for follower in followers]
        follower_objects = User.query.filter(User.id.in_(folower_objects_count)).all()
        followersCount = len(folower_objects_count)
        print(follower_objects)
        if 'likedANote' in request.form:
            note_id = request.form.get('likedANote')
            isLiked = likesNotes.query.filter_by(user_id=current_user.id, note_id=note_id).first()
            if isLiked:
                Notes.query.filter_by(id=note_id).first().likesCountNotes -= 1
                likesNotes.query.filter_by(note_id=note_id, user_id=current_user.id).delete()
                db.session.commit()
            else:
                Notes.query.filter_by(id=note_id).first().likesCountNotes += 1
                new_like = likesNotes(user_id=current_user.id, note_id=note_id)
                db.session().add(new_like)
                db.session.commit()
            user_likes_notes = [likes.note_id for likes in likesNotes.query.filter_by(user_id=current_user.id).all()]



        if 'likedATest' in request.form:
            test_id = request.form.get('likedATest')
            isLiked = likesTests.query.filter_by(user_id=current_user.id, test_id=test_id).first()
            if isLiked:
                Tests.query.filter_by(id=test_id).first().likesCountTests -= 1
                likesTests.query.filter_by(test_id=test_id, user_id=current_user.id).delete()
                db.session.commit()
            else:
                Tests.query.filter_by(id=test_id).first().likesCountTests += 1
                new_like = likesTests(user_id=current_user.id, test_id=test_id)
                db.session().add(new_like)
                db.session.commit()
            user_likes_tests = [likes.test_id for likes in likesTests.query.filter_by(user_id=current_user.id).all()]

        if 'likedACard' in request.form:
            card_id = request.form.get('likedACard')
            isLiked = likesCards.query.filter_by(user_id=current_user.id, card_id=card_id).first()
            if isLiked:
                Qcards.query.filter_by(id=card_id).first().likesCountCards -= 1
                likesCards.query.filter_by(card_id=card_id, user_id=current_user.id).delete()
                db.session.commit()
            else:
                Qcards.query.filter_by(id=card_id).first().likesCountCards += 1
                new_like = likesCards(user_id=current_user.id, card_id=card_id)
                db.session().add(new_like)
                db.session.commit()
            user_likes_cards = [likes.card_id for likes in likesCards.query.filter_by(user_id=current_user.id).all()]

    return render_template('seeMore.html', user=current_user, mainClass=main_class, mainClassOther=Notes.query.filter_by(class_id=main_class.id),  mainClassNotes=reversed(Notes.query.filter_by(class_id=main_class.id).order_by(Notes.likesCountNotes).all()), mainClassTests=Tests.query.filter_by(class_id=main_class.id), mainClassCards=Qcards.query.filter_by(class_id=main_class.id), sum=sum, followedClassesMain=followedClasses, followersCount=followersCount, user_likes_notes=user_likes_notes, user_likes_tests=user_likes_tests, user_likes_cards=user_likes_cards, WebsiteName=WebsiteName, follower_objects=follower_objects)

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    postedNotesCount = Notes.query.filter_by(user_id=current_user.id).count()
    postedTestsCount = Tests.query.filter_by(user_id=current_user.id).count()
    postedCardsCount = Qcards.query.filter_by(user_id=current_user.id).count()

    postedNotes = Notes.query.filter_by(user_id=current_user.id).all()
    postedTests = Tests.query.filter_by(user_id=current_user.id).all()
    postedCards = Qcards.query.filter_by(user_id=current_user.id).all()

    Messages = reversed(Message.query.all())

    following_ids = [following.class_id for following in Following.query.filter_by(user_id=current_user.id).all()]
    followedClasses = Class.query.filter(Class.id.in_(following_ids)).all()

    following_ids_friends = [following.user_id for following in FollowingUser.query.filter_by(user_id_followed=current_user.id).all()]
    all_friends = User.query.filter(User.id.in_(following_ids_friends)).all()
    followers_count = FollowingUser.query.filter_by(user_id_followed=current_user.id).count()

    print(all_friends, "--------------")


    if request.method == 'POST':
        print('----------------------------test')
        if 'newEmail' in request.form:
            newEmail = request.form.get('newEmail').lower()
            userCheck = User.query.filter_by(email = newEmail).first()
            if userCheck:
                flash("email in use by another user", category='error')
            else:
                User.query.filter_by(id=current_user.id).first().email = newEmail
                db.session.commit()
                flash("email changed", category='success')
        elif 'newUsername' in request.form:
            newUsername = request.form.get('newUsername').lower()
            userCheck = User.query.filter_by(username = newUsername).first()
            if userCheck:
                flash("Username in Use", category='error')
            else:
                User.query.filter_by(id=current_user.id).first().username  = newUsername
                db.session.commit()
                flash("username changed", category='success')
        elif 'currentPassword' in request.form:
            currentPassword = request.form.get('currentPassword')
            newPassword = request.form.get('newPassword')
            confirmNewPassword = request.form.get('confirmNewPassword')
            if not check_password_hash(current_user.password, currentPassword):
                flash("incorrect password", category='error')
            elif newPassword != confirmNewPassword:
                flash("passwords dont match", category='error')
            elif len(newPassword) < 7:
                flash("password to short", category='error')
            else:
                User.query.filter_by(id=current_user.id).first().password = generate_password_hash(newPassword, method='pbkdf2:sha256')
                db.session.commit()
        elif 'deleteNote' in request.form:
            Notes.query.filter_by(id=request.form.get('deleteNote')).delete()
            likesNotes.query.filter_by(note_id=request.form.get('deleteNote')).delete()
            db.session.commit()
            postedNotesCount = Notes.query.filter_by(user_id=current_user.id).count()
            postedNotes = Notes.query.filter_by(user_id=current_user.id).all()

        elif 'deleteTest' in request.form:
            Tests.query.filter_by(id=request.form.get('deleteTest')).delete()
            db.session.commit()
            postedTestsCount = Tests.query.filter_by(user_id=current_user.id).count()
            postedTests = Tests.query.filter_by(user_id=current_user.id).all()

        elif 'deleteCard' in request.form:
            Qcards.query.filter_by(id=request.form.get('deleteCard')).delete()
            db.session.commit()
            postedCardsCount = Qcards.query.filter_by(user_id=current_user.id).count()
            postedCards = Qcards.query.filter_by(user_id=current_user.id).all()


    return render_template('profile.html', user=current_user, submission=postedNotesCount+postedCardsCount+postedTestsCount, Notes=postedNotes, Tests=postedTests, Cards=postedCards, followedClassesMain=followedClasses, followingCount=len(followedClasses), WebsiteName=WebsiteName, Messages=Messages, all_friends=all_friends, followers_count=followers_count)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        print('----------------------------test')
        if 'newEmail' in request.form:
            newEmail = request.form.get('newEmail')
            userCheck = User.query.filter_by(email = newEmail).first()
            if userCheck:
                flash("email in use by another user", category='error')
            else:
                User.query.filter_by(id=current_user.id).first().email = newEmail
                db.session.commit()
                flash("email changed", category='success')
        elif 'newUsername' in request.form:
            newUsername = request.form.get('newUsername')
            userCheck = User.query.filter_by(username = newUsername).first()
            if userCheck:
                flash("Username in Use", category='error')
            else:
                User.query.filter_by(id=current_user.id).first().username  = newUsername
                db.session.commit()
                flash("username changed", category='success')

        elif 'currentPassword' in request.form:
            currentPassword = request.form.get('currentPassword')
            newPassword = request.form.get('newPassword')
            confirmNewPassword = request.form.get('confirmNewPassword')
            if not check_password_hash(current_user.password, currentPassword):
                flash("incorrect password", category='error')
            elif newPassword != confirmNewPassword:
                flash("passwords dont match", category='error')
            elif len(newPassword) < 7:
                flash("password to short", category='error')
            else:
                User.query.filter_by(id=current_user.id).first().password = generate_password_hash(newPassword, method='pbkdf2:sha256')
                db.session.commit()
                flash("password changed", category='success')

        elif 'visibility' in request.form:
            v = request.form.get('visibility')
            if v == 'yes':
                current_user.is_visible = True
                db.session.commit()
            else:
                current_user.is_visible = False
                db.session.commit()


    return render_template('settings.html', user=current_user, WebsiteName=WebsiteName)

@views.route('/follow', methods=['GET', 'POST'])
@login_required
def follow():
    if request.method == 'POST':
        class_id = request.form.get('classid')
        followingCheck = Following.query.filter_by(user_id=current_user.id, class_id=class_id).first()

        if followingCheck:
            currentFollow = Following.query.filter_by(user_id=current_user.id, class_id=class_id).first()
            db.session().delete(currentFollow)
            Class.query.filter_by(id=class_id).first().following_count -= 1
            db.session.commit()
        else:
            newFollow = Following(user_id=current_user.id, class_id=class_id)
            db.session().add(newFollow)
            Class.query.filter_by(id=class_id).first().following_count += 1
            db.session.commit()

            #print(newFollow.user_id ,  " ---------------------is following ", newFollow.class_id)

    return redirect(url_for('views.home'))

@views.route('/wfguwfuwfnfwvhuhsvsfsvfsvffxasqqdxj', methods=['GET', 'POST'])
@login_required
def deleteAccount():
    user = User.query.filter_by(id=current_user.id).delete()
    print('-----deleted--------')
    db.session.commit()
    return redirect(url_for('auth.logout'))


@views.route('/landing')
def landingPage():
    return render_template('landing.html', count=User.query.filter_by().count() + 3, WebsiteName=WebsiteName)

@views.route('/reviews', methods=['GET', 'POST'])
def reviewsPage():
    if request.method == 'POST':
        # Get all form data
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        # Process the form data here (e.g., store it in a database)
        new_review = Reviews(rating=rating, comment=comment, user_id=current_user.id)

        if Reviews.query.filter_by(user_id=current_user.id).first():
            db.session().delete(Reviews.query.filter_by(user_id=current_user.id).first())
            db.session().add(new_review)
            flash("We've updated your review")
        else:
            db.session().add(new_review)
            if(int(rating) < 3):
                flash("Were working on getting better")
            else:
                flash("Thanks for the review!")


        db.session.commit()

        return render_template('reviews.html', message="Review submitted successfully!", WebsiteName=WebsiteName)
    else:
        return render_template('reviews.html', WebsiteName=WebsiteName)


@views.route('/searchClass', methods=['GET', 'POST'])
def searchClass():

    if request.method == 'POST':
        following_ids = [following.class_id for following in Following.query.filter_by(user_id=current_user.id).all()]

        # Filter classes based on the user's following relationships
        followedClasses = Class.query.filter(Class.id.in_(following_ids)).all()



        if 'follow' in request.form:
            cname = request.form.get('searchName')
            cid = Class.query.filter_by(name=cname).first().id
            followingCheck = Following.query.filter_by(user_id=current_user.id, class_id=cid).first()
            if followingCheck:
                currentFollow = Following.query.filter_by(user_id=current_user.id, class_id=cid).first()
                db.session().delete(currentFollow)
                Class.query.filter_by(id=cid).first().following_count -= 1
                db.session.commit()
            else:
                newFollow = Following(user_id=current_user.id, class_id=cid)
                db.session().add(newFollow)
                Class.query.filter_by(id=cid).first().following_count += 1
                db.session.commit()

        following_ids = [following.class_id for following in Following.query.filter_by(user_id=current_user.id).all()]

        searchName = request.form.get('searchName')  # Use request.form.get for POST requests
        search_results = Class.query.filter(func.lower(Class.name) == func.lower(searchName)).all()
        print("search results: ", search_results)
        if not search_results:
            flash("No class found, Want to create it?", category='error')
            search_results = Class.query.all()
            isClass = False
        else:
            isClass = True


        return render_template('searchClass.html', matches=search_results, followedClassesMain=Class.query.filter(Class.id.in_(following_ids)).all(), isClass=isClass, name=searchName, WebsiteName=WebsiteName)

    return render_template('searchClass.html', followedClassesMain=Class.query.filter(Class.id.in_(following_ids)).all(), WebsiteName=WebsiteName)



@views.route('/<path:path>')
@login_required
def get_dir(path):
    if 'adjbawfjciwc' in path:
        return redirect(url_for('views.home'))


    return send_from_directory('../../',  path)

@views.route('/adminBoard', methods=['GET', 'POST'])
@login_required
def adminBoard():
    if request.method == "POST":
        usernameTest = request.form.get('username')
        passwordTest = request.form.get('password')
        keyword = request.form.get('keyword')
        subject = request.form.get('subject')
        message = request.form.get('message')

        admin = User.query.filter_by(username='kha157').first()
        if 'keyword' in request.form:
            if check_password_hash(admin.password, passwordTest):
                if usernameTest == admin.username:
                    if keyword  == 'kittcatthekittycatthechristmascat':
                        messageMain = Message(title=subject, body=message)
                        db.session().add(messageMain)
                        db.session.commit()
                    else:
                        print("keyword wrong")
                else:
                    print("username wrong")
            else:
                print("Password wrong")
        if 'classRemove' in request.form:
            class_id = request.form.get('classRemove')
            Class.query.filter_by(id=class_id).delete()
            db.session.commit()

        elif 'notesRemove' in request.form:
            note_id = request.form.get('notesRemove')
            print("note id", note_id)
            Notes.query.filter_by(id=note_id).delete()
            db.session.commit()

        elif 'testsRemove' in request.form:
            note_id = request.form.get('testsRemove')
            Tests.query.filter_by(id=note_id).delete()
            db.session.commit()

        elif 'cardsRemove' in request.form:
            note_id = request.form.get('cardsRemove')
            Qcards.query.filter_by(id=note_id).delete()
            db.session.commit()


        elif 'messageRemove' in request.form:
            note_id = request.form.get('messageRemove')
            Message.query.filter_by(id=note_id).delete()
            db.session.commit()



    if current_user.id == 1 and current_user.username == "kha157":
        return render_template('adminPage.html', allClasses = Class.query.all(), allNotes = Notes.query.all(), allTests = Tests.query.all(), allCards = Qcards.query.all(), reviewsAll=Reviews.query.all(), numberOfMembers=User.query.count(), Messages = reversed(Message.query.all()))
    else:
        return redirect(url_for('views.home'))


@views.route('/disscusion', methods=['GET', 'POST'])
@login_required
def disscusionPage():
    if request.method == "POST":
        print("Follow Runs")
    return render_template('discussions.html')



@views.route('/profileOther', methods=['GET', 'POST'])
@login_required
def profileOther():
    if request.method == 'POST':
        other_user_id = request.form.get('user_id_other')
        UserCurrent = User.query.filter_by(id=other_user_id).first()
        postedNotesCount = Notes.query.filter_by(user_id=other_user_id).count()
        postedTestsCount = Tests.query.filter_by(user_id=other_user_id).count()
        postedCardsCount = Qcards.query.filter_by(user_id=other_user_id).count()

        postedNotes = Notes.query.filter_by(user_id=other_user_id).all()
        postedTests = Tests.query.filter_by(user_id=other_user_id).all()
        postedCards = Qcards.query.filter_by(user_id=other_user_id).all()



        following_ids = [following.class_id for following in Following.query.filter_by(user_id=other_user_id).all()]
        followedClasses = Class.query.filter(Class.id.in_(following_ids)).all()
        print("got here before")
        following_ids = [following.user_id_followed for following in FollowingUser.query.filter_by(user_id=current_user.id).all()]

        if 'follow_user_other' in request.form:
            print("got here")
            # Check if the user is already following the other user
            new_user_follow_check = FollowingUser.query.filter_by(user_id=current_user.id, user_id_followed=other_user_id).first()
            if new_user_follow_check:
                print("unfollow")
                # Delete the follow relationship
                db.session.delete(new_user_follow_check)
                db.session.commit()
            else:
                print("follow")
                # Create a new follow relationship
                new_user_follow = FollowingUser(user_id=current_user.id, user_id_followed=other_user_id)
                db.session.add(new_user_follow)
                db.session.commit()




            following_ids = [following.user_id_followed for following in FollowingUser.query.filter_by(user_id=current_user.id).all()]

    followers_count = FollowingUser.query.filter_by(user_id_followed=other_user_id).count()


    print("who following:  ", following_ids)
    return render_template('profileOther.html', user=UserCurrent, submission=postedNotesCount+postedCardsCount+postedTestsCount, Notes=postedNotes, Tests=postedTests, Cards=postedCards, followedClassesMain=followedClasses, followingCount=len(followedClasses), WebsiteName=WebsiteName, followedUserMain=following_ids, followers_count=followers_count)


@views.route('/allUsers', methods=['GET', 'POST'])
@login_required
def allUsers():
    return render_template('allUsers.html', users_all=User.query.filter_by(is_visible=True).all(), WebsiteName=WebsiteName, users_count=User.query.filter_by(is_visible=True).count(), title="Members of The Study Resource")



@views.route('/questionBoard', methods=['GET', 'POST'])
@login_required
def questionBoard():
    if request.method == 'POST':

        if 'delete_question' in request.form:
            question_id = request.form.get('question_id')
            Question.query.filter_by(id=question_id).delete()
            db.session.commit()

        class_id = request.form.get('class_id')

        main_class = Class.query.filter_by(id=class_id).first()
        all_questions = Question.query.filter_by(class_id=class_id).order_by(desc(Question.timestamp)).all()

        my_questions = Question.query.filter_by(class_id=class_id, user_id=current_user.id).order_by(desc(Question.timestamp)).all()
        for question in all_questions:
            question.user = User.query.get(question.user_id)  # Assuming User is the name of your User model
            question.formatted_timestamp = question.timestamp.strftime("%b %d, %Y at %I:%M %p")
            print(question.user)


    return render_template('questionBoard.html', current_user=current_user, main_class=main_class, all_questions=all_questions, my_questions=my_questions)


@views.route('/askQuestion', methods=['GET', 'POST'])
@login_required
def askQuestion():
    if request.method == 'POST':
        class_name=request.form.get("class_name")
        class_id = Class.query.filter_by(name=class_name).first().id

        title = request.form.get('title')
        content = request.form.get('content')

        new_question = Question(user_id=current_user.id, class_id=class_id, title=title, content=content, timestamp=datetime.now())
        db.session.add(new_question)
        db.session.commit()


    return render_template('askQuestion.html', classesForward=Class.query.all())


@views.route('/questionSeeMore', methods=['GET', 'POST'])
@login_required
def questionSeeMore():
    if request.method == 'POST':
        if 'postAnswer' in request.form:
            content = request.form.get('content')
            question_id = request.form.get('question_id')
            print(question_id)
            new_answer = Answer(user_id=current_user.id, question_id=question_id, content=content, timestamp=datetime.now())
            db.session.add(new_answer)
            db.session.commit()

        if 'delete' in request.form:
            answer_id = request.form.get('delete')
            Answer.query.filter_by(id=answer_id).delete()
            db.session.commit()

        question_id = request.form.get('question_id')
        main_question = Question.query.filter_by(id=question_id).first()
        main_question.formatted_timestamp = main_question.timestamp.strftime("%b %d, %Y at %I:%M %p")
        main_question.posted_by = User.query.filter_by(id=main_question.user_id).first()
        all_answers = Answer.query.filter_by(question_id=question_id).order_by(desc(Answer.timestamp)).all()

        for answer in all_answers:
            answer.postedBy = User.query.filter_by(id=answer.user_id).first()  # Assuming User is the name of your User model
            answer.formatted_timestamp = answer.timestamp.strftime("%b %d, %Y at %I:%M %p")


    return render_template('questionSeeMore.html', all_answers=all_answers, main_question=main_question, count=Answer.query.filter_by(question_id=question_id).count(), current_user=current_user)


