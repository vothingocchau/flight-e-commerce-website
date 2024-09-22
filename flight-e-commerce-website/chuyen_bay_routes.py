from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from db_utils import cursor, db

chuyen_bay_routes = Blueprint('chuyen_bay_routes', __name__)


@chuyen_bay_routes.route('/them_chuyen_bay', methods=['GET', 'POST'])
def them_chuyen_bay():
    if request.method == 'GET':
        # Lấy danh sách chuyến bay từ cơ sở dữ liệu
        cursor.execute("SELECT * FROM san_bay")
        danh_sach_san_bay = cursor.fetchall()
        quyen = session['user']['vai_tro'] or 'Khách hàng'
        return render_template('them_chuyen_bay.html', danh_sach_san_bay=danh_sach_san_bay, quyen=quyen)

    elif request.method == 'POST':
        # Lấy thông tin từ form
        ma_chuyen_bay = request.form['ma_chuyen_bay']
        san_bay_di = request.form['san_bay_di']
        san_bay_den = request.form['san_bay_den']

        try:
            # Thực hiện chèn dữ liệu vào bảng chuyen_bay
            cursor.execute("INSERT INTO chuyen_bay (ma_chuyen_bay, san_bay_di, san_bay_den) VALUES (%s, %s, %s)",
                           (ma_chuyen_bay, san_bay_di, san_bay_den))
            db.commit()
            # Thêm vé Hạng 1
            cursor.execute("INSERT INTO ve_chuyen_bay (ma_chuyen_bay, hang_ve, gia) VALUES (%s, %s, %s)",
                           (ma_chuyen_bay, 'Hạng 1', 1500000))
            db.commit()

            # Thêm vé Hạng 2
            cursor.execute("INSERT INTO ve_chuyen_bay (ma_chuyen_bay, hang_ve, gia) VALUES (%s, %s, %s)",
                           (ma_chuyen_bay, 'Hạng 2', 800000))
            db.commit()
            flash('Thêm chuyến bay thành công!')
            return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}')
    quyen = session['user']['vai_tro'] or 'Khách hàng'
    return render_template('them_chuyen_bay.html', quyen=quyen)


@chuyen_bay_routes.route('/sua_chuyen_bay/<ma_chuyen_bay>', methods=['GET', 'POST'])
def sua_chuyen_bay(ma_chuyen_bay):
    if request.method == 'GET':
        # Lấy thông tin chuyến bay từ cơ sở dữ liệu
        cursor.execute("SELECT san_bay_di, san_bay_den FROM chuyen_bay WHERE ma_chuyen_bay = %s", (ma_chuyen_bay,))
        chuyen_bay = cursor.fetchone()

        if chuyen_bay:
            # Lấy danh sách sân bay từ cơ sở dữ liệu
            cursor.execute("SELECT * FROM san_bay")
            danh_sach_san_bay = cursor.fetchall()
            quyen = session['user']['vai_tro'] or 'Khách hàng'
            return render_template('sua_chuyen_bay.html', chuyen_bay=chuyen_bay, danh_sach_san_bay=danh_sach_san_bay,
                                   quyen=quyen)
        else:
            flash('Chuyến bay không tồn tại!')

            return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))

    elif request.method == 'POST':
        # Lấy thông tin từ form
        san_bay_di_moi = request.form['san_bay_di']
        san_bay_den_moi = request.form['san_bay_den']

        try:
            # Thực hiện cập nhật thông tin chuyen_bay trong cơ sở dữ liệu
            cursor.execute("UPDATE chuyen_bay SET san_bay_di = %s, san_bay_den = %s WHERE ma_chuyen_bay = %s",
                           (san_bay_di_moi, san_bay_den_moi, ma_chuyen_bay))
            db.commit()

            flash('Cập nhật chuyến bay thành công!')
            return redirect(url_for('danh_sach_chuyen_bay'))

        except Exception as e:
            # Xử lý lỗi, ví dụ: log lỗi hoặc trả về một trang lỗi
            flash(f'Có lỗi xảy ra: {str(e)}')
            return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))


@chuyen_bay_routes.route('/xoa_chuyen_bay/<ma_chuyen_bay>')
def xoa_chuyen_bay(ma_chuyen_bay):
    try:
        # Thực hiện xóa chuyến bay khỏi cơ sở dữ liệu
        cursor.execute("DELETE FROM chuyen_bay WHERE ma_chuyen_bay = %s", (ma_chuyen_bay,))
        db.commit()

        flash('Xóa chuyến bay thành công!')
    except Exception as e:
        # Xử lý lỗi, ví dụ: log lỗi hoặc trả về một trang lỗi
        flash(f'Có lỗi xảy ra: {str(e)}')

    return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))


@chuyen_bay_routes.route('/danh_sach_chuyen_bay')
def danh_sach_chuyen_bay():
    # Lấy danh sách chuyến bay từ cơ sở dữ liệu
    quyen = session['user']['vai_tro'] or 'Khách hàng'
    cursor.execute("SELECT * FROM chuyen_bay")
    chuyen_bay_list = cursor.fetchall()
    return render_template('danh_sach_chuyen_bay.html', chuyen_bay_list=chuyen_bay_list, quyen=quyen)
