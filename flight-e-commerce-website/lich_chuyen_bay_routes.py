from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from db_utils import cursor, db

lich_chuyen_bay_routes = Blueprint('lich_chuyen_bay_routes', __name__)


@lich_chuyen_bay_routes.route('/lich_chuyen_bay/<ma_chuyen_bay>', methods=['GET', 'POST'])
def lich_chuyen_bay(ma_chuyen_bay):
    if request.method == 'GET':
        # Lấy thông tin lịch chuyến bay từ cơ sở dữ liệu
        # Sử dụng mã chuyến bay để lọc các lịch chuyến bay tương ứng
        cursor.execute("SELECT * FROM lich_chuyen_bay WHERE ma_chuyen_bay = %s", (ma_chuyen_bay,))
        lich_chuyen_bay_list = cursor.fetchall()
        quyen = session['user']['vai_tro'] or 'Khách hàng'
        return render_template('lich_chuyen_bay.html', lich_chuyen_bay_list=lich_chuyen_bay_list,
                               ma_chuyen_bay=ma_chuyen_bay, quyen=quyen)


@lich_chuyen_bay_routes.route('/them_lich_chuyen_bay/<ma_chuyen_bay>', methods=['GET', 'POST'])
def them_lich_chuyen_bay(ma_chuyen_bay):
    if request.method == 'POST':
        # Lấy thông tin từ form
        ngay_gio_khoi_hanh = request.form['ngay_gio_khoi_hanh']
        thoi_gian_bay_phut = request.form['thoi_gian_bay_phut']
        so_ghe_hang_1 = request.form['so_ghe_hang_1']
        so_ghe_hang_2 = request.form['so_ghe_hang_2']

        try:
            # Thực hiện chèn dữ liệu vào bảng lich_chuyen_bay
            cursor.execute(
                "INSERT INTO lich_chuyen_bay (ma_chuyen_bay, ngay_gio_khoi_hanh, thoi_gian_bay_phut, so_ghe_hang_1, so_ghe_hang_2) VALUES (%s, %s, %s, %s, %s)",
                (ma_chuyen_bay, ngay_gio_khoi_hanh, thoi_gian_bay_phut, so_ghe_hang_1, so_ghe_hang_2))
            db.commit()

            # Lấy ID của lịch chuyến bay vừa thêm
            cursor.execute("SELECT LAST_INSERT_ID()")
            last_insert_id = cursor.fetchone()[0]

            # Thêm sân bay trung gian
            stt_list = request.form.getlist('stt[]')
            san_bay_trung_gian_list = request.form.getlist('san_bay_trung_gian[]')
            thoi_gian_dung_phut_list = request.form.getlist('thoi_gian_dung_phut[]')
            ghi_chu_list = request.form.getlist('ghi_chu[]')

            for stt, san_bay, thoi_gian, ghi_chu in zip(stt_list, san_bay_trung_gian_list, thoi_gian_dung_phut_list,
                                                        ghi_chu_list):
                cursor.execute(
                    "INSERT INTO san_bay_trung_gian (stt, ma_lich_chuyen_bay, san_bay_trung_gian, thoi_gian_dung_phut, ghi_chu) VALUES (%s, %s, %s, %s, %s)",
                    (stt, last_insert_id, san_bay, thoi_gian, ghi_chu))
                db.commit()

            flash('Thêm lịch chuyến bay thành công!')
            return redirect(url_for('lich_chuyen_bay_routes.lich_chuyen_bay', ma_chuyen_bay=ma_chuyen_bay))

        except Exception as e:
            # Xử lý lỗi, ví dụ: log lỗi hoặc trả về một trang lỗi
            flash(f'Có lỗi xảy ra: {str(e)}')

    # Truy vấn danh sách sân bay để hiển thị trong dropdown
    cursor.execute("SELECT * FROM san_bay")
    danh_sach_san_bay = cursor.fetchall()
    # Truy vấn thông tin quy định
    cursor.execute("SELECT * FROM quy_dinh")
    quy_dinh_info = cursor.fetchone()

    quyen = session['user']['vai_tro'] or 'Khách hàng'
    return render_template('them_lich_chuyen_bay.html', ma_chuyen_bay=ma_chuyen_bay,
                           danh_sach_san_bay=danh_sach_san_bay, quy_dinh_info=quy_dinh_info, quyen=quyen)


@lich_chuyen_bay_routes.route('/sua_lich_chuyen_bay/<ma_lich_chuyen_bay>', methods=['GET', 'POST'])
def sua_lich_chuyen_bay(ma_lich_chuyen_bay):
    cursor.execute("SELECT ma_chuyen_bay FROM lich_chuyen_bay WHERE ma_lich_chuyen_bay = %s", (ma_lich_chuyen_bay,))
    ma_chuyen_bay = cursor.fetchone()[0]

    if request.method == 'GET':
        # Lấy thông tin lịch chuyến bay từ cơ sở dữ liệu
        cursor.execute("SELECT * FROM lich_chuyen_bay WHERE ma_lich_chuyen_bay = %s", (ma_lich_chuyen_bay,))
        lich_chuyen_bay = cursor.fetchone()

        if lich_chuyen_bay:
            # Lấy thông tin sân bay trung gian từ cơ sở dữ liệu
            cursor.execute("SELECT * FROM san_bay_trung_gian WHERE ma_lich_chuyen_bay = %s", (ma_lich_chuyen_bay,))
            danh_sach_san_bay_trung_gian = cursor.fetchall()
            cursor.execute("SELECT * FROM san_bay")
            danh_sach_san_bay = cursor.fetchall()
            cursor.execute("SELECT * FROM quy_dinh")
            quy_dinh_info = cursor.fetchone()
            quyen = session['user']['vai_tro'] or 'Khách hàng'
            return render_template('sua_lich_chuyen_bay.html', lich_chuyen_bay=lich_chuyen_bay,
                                   danh_sach_san_bay_trung_gian=danh_sach_san_bay_trung_gian,
                                   danh_sach_san_bay=danh_sach_san_bay, quyen=quyen, quy_dinh_info=quy_dinh_info)
        else:
            flash('Lịch chuyến bay không tồn tại!')
            return redirect(url_for('lich_chuyen_bay_routes.lich_chuyen_bay', ma_chuyen_bay=ma_chuyen_bay))

    elif request.method == 'POST':
        # Lấy thông tin từ form
        ngay_gio_khoi_hanh = request.form['ngay_gio_khoi_hanh']
        thoi_gian_bay_phut = request.form['thoi_gian_bay_phut']
        so_ghe_hang_1 = request.form['so_ghe_hang_1']
        so_ghe_hang_2 = request.form['so_ghe_hang_2']

        try:
            # Thực hiện cập nhật thông tin lich_chuyen_bay trong cơ sở dữ liệu
            cursor.execute(
                "UPDATE lich_chuyen_bay SET ngay_gio_khoi_hanh = %s, thoi_gian_bay_phut = %s, so_ghe_hang_1 = %s, so_ghe_hang_2 = %s WHERE ma_lich_chuyen_bay = %s",
                (ngay_gio_khoi_hanh, thoi_gian_bay_phut, so_ghe_hang_1, so_ghe_hang_2, ma_lich_chuyen_bay))
            db.commit()

            # Lấy danh sách các sân bay trung gian cũ để xóa trước khi thêm mới
            cursor.execute("DELETE FROM san_bay_trung_gian WHERE ma_lich_chuyen_bay = %s", (ma_lich_chuyen_bay,))
            db.commit()

            # Thêm sân bay trung gian mới
            stt_list = request.form.getlist('stt[]')
            san_bay_trung_gian_list = request.form.getlist('san_bay_trung_gian[]')
            thoi_gian_dung_phut_list = request.form.getlist('thoi_gian_dung_phut[]')
            ghi_chu_list = request.form.getlist('ghi_chu[]')

            for stt, san_bay, thoi_gian, ghi_chu in zip(stt_list, san_bay_trung_gian_list, thoi_gian_dung_phut_list,
                                                        ghi_chu_list):
                cursor.execute(
                    "INSERT INTO san_bay_trung_gian (stt, ma_lich_chuyen_bay, san_bay_trung_gian, thoi_gian_dung_phut, ghi_chu) VALUES (%s, %s, %s, %s, %s)",
                    (stt, ma_lich_chuyen_bay, san_bay, thoi_gian, ghi_chu))
                db.commit()

            flash('Cập nhật lịch chuyến bay thành công!')
            # Chuyển hướng về trang lich_chuyen_bay với ma_chuyen_bay
            return redirect(url_for('lich_chuyen_bay_routes.lich_chuyen_bay', ma_chuyen_bay=ma_chuyen_bay))

        except Exception as e:
            # Xử lý lỗi, ví dụ: log lỗi hoặc trả về một trang lỗi
            flash(f'Có lỗi xảy ra: {str(e)}')
            # Chuyển hướng về trang lich_chuyen_bay nếu có lỗi
            return redirect(url_for('lich_chuyen_bay_routes.lich_chuyen_bay', ma_chuyen_bay=ma_chuyen_bay))


@lich_chuyen_bay_routes.route('/xoa_lich_chuyen_bay/<ma_lich_chuyen_bay>')
def xoa_lich_chuyen_bay(ma_lich_chuyen_bay):
    # Lấy mã chuyến bay của lịch vừa xóa
    cursor.execute("SELECT ma_chuyen_bay FROM lich_chuyen_bay WHERE ma_lich_chuyen_bay = %s", (ma_lich_chuyen_bay,))
    ma_chuyen_bay = cursor.fetchone()[0]
    try:

        # Thực hiện xóa lịch chuyến bay khỏi cơ sở dữ liệu
        cursor.execute("DELETE FROM lich_chuyen_bay WHERE ma_lich_chuyen_bay = %s", (ma_lich_chuyen_bay,))
        db.commit()

        flash('Xóa lịch chuyến bay thành công!')
    except Exception as e:
        # Xử lý lỗi, ví dụ: log lỗi hoặc trả về một trang lỗi
        flash(f'Có lỗi xảy ra: {str(e)}')

    return redirect(url_for('lich_chuyen_bay_routes.lich_chuyen_bay', ma_chuyen_bay=ma_chuyen_bay))

