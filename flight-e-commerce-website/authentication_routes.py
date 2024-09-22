from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from db_utils import authenticate_user

authentication_routes = Blueprint('authentication_routes', __name__)


@authentication_routes.route('/')
def index():
    # Clear the 'user' key from the session
    session.pop('user', None)

    # Set 'user' key to an empty dictionary
    session['user'] = {'ma_nguoi_dung': "No", 'ten_nguoi_dung': "No", 'vai_tro': "Khách hàng"}
    return render_template('index.html')


@authentication_routes.route('/dang_nhap', methods=['GET', 'POST'])
def dang_nhap():
    if request.method == 'POST':
        username = request.form['ma_nguoi_dung']
        password = request.form['mat_khau']

        # Kiểm tra xác thực người dùng
        user = authenticate_user(username, password)

        if user:
            # Lưu thông tin người dùng vào session
            session['user'] = {'ma_nguoi_dung': user[0], 'ten_nguoi_dung': user[1], 'vai_tro': user[3]}
            flash('Đăng nhập thành công!', 'success')

            # Chuyển hướng đến trang chính tùy thuộc vào vai trò của người dùng
            if user[3] == 'Admin':
                return redirect(url_for('.trang_admin'))
            elif user[3] == 'Nhân viên':
                return redirect(url_for('.trang_nhan_vien'))
        else:
            flash('Đăng nhập thất bại. Vui lòng kiểm tra lại tên đăng nhập và mật khẩu.', 'error')

    return render_template('dang_nhap.html')


@authentication_routes.route('/trang_admin')
def trang_admin():
    # Kiểm tra xem người dùng đã đăng nhập với vai trò Admin chưa
    if 'user' in session and session['user']['vai_tro'] == 'Admin':
        quyen = session['user']['vai_tro'] or 'Khách hàng'
        return render_template('trang_admin.html', quyen=quyen)
    else:
        flash('Truy cập bị từ chối. Vui lòng đăng nhập với tư cách Admin.', 'error')
        return redirect(url_for('.dang_nhap'))


@authentication_routes.route('/trang_nhan_vien')
def trang_nhan_vien():
    # Kiểm tra xem người dùng đã đăng nhập với vai trò Nhân viên chưa
    if 'user' in session and session['user']['vai_tro'] == 'Nhân viên':
        quyen = session['user']['vai_tro'] or 'Khách hàng'
        return render_template('trang_nhan_vien.html', quyen=quyen)
    else:
        flash('Truy cập bị từ chối. Vui lòng đăng nhập với tư cách Nhân viên.', 'error')
        return redirect(url_for('.dang_nhap'))


@authentication_routes.route('/trang_khach_hang')
def trang_khach_hang():
    quyen = session['user']['vai_tro'] or 'Khách hàng'
    return render_template('trang_khach_hang.html', quyen=quyen)
