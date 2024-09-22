from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from db_utils import cursor, db
from datetime import datetime, timedelta

ban_ve_routes = Blueprint('ban_ve_routes', __name__)


@ban_ve_routes.route('/danh_sach_ban_ve')
def danh_sach_ban_ve():
    cursor.execute(
        "SELECT DISTINCT ma_san_bay, ten_san_bay FROM (SELECT san_bay.ma_san_bay, san_bay.ten_san_bay FROM chuyen_bay JOIN san_bay ON chuyen_bay.san_bay_di = san_bay.ma_san_bay) AS subquery")
    danh_sach_san_bay_di = [row for row in cursor.fetchall()]

    cursor.execute(
        "SELECT DISTINCT ma_san_bay, ten_san_bay FROM (SELECT san_bay.ma_san_bay, san_bay.ten_san_bay FROM chuyen_bay JOIN san_bay ON chuyen_bay.san_bay_den = san_bay.ma_san_bay) AS subquery")
    danh_sach_san_bay_den = [row for row in cursor.fetchall()]

    # Lấy thông tin từ form nếu có
    san_bay_di_selected = request.args.get('san_bay_di', '')
    san_bay_den_selected = request.args.get('san_bay_den', '')
    ngay_khoi_hanh = request.args.get('ngay_khoi_hanh', '')

    # Tìm chuyến bay theo điều kiện tìm kiếm
    chuyen_bay_list = []
    query = "SELECT chuyen_bay.ma_chuyen_bay, chuyen_bay.san_bay_di, chuyen_bay.san_bay_den, lich_chuyen_bay.ngay_gio_khoi_hanh, ve_chuyen_bay.gia, ve_chuyen_bay.ma_ve, ve_chuyen_bay.hang_ve, lich_chuyen_bay.ma_lich_chuyen_bay FROM lich_chuyen_bay INNER JOIN chuyen_bay ON lich_chuyen_bay.ma_chuyen_bay = chuyen_bay.ma_chuyen_bay JOIN ve_chuyen_bay ON chuyen_bay.ma_chuyen_bay = ve_chuyen_bay.ma_chuyen_bay "
    params = []
    if san_bay_di_selected:
        query += " WHERE chuyen_bay.san_bay_di = %s"
        params.append(san_bay_di_selected)

    if san_bay_den_selected:
        query += " AND chuyen_bay.san_bay_den = %s"
        params.append(san_bay_den_selected)

    if ngay_khoi_hanh:
        query += " AND DATE(lich_chuyen_bay.ngay_gio_khoi_hanh) LIKE %s"
        params.append(f"{ngay_khoi_hanh}%")
    if ngay_khoi_hanh:
        if params:
            query += " AND"
        else:
            query += " WHERE"

        # Thêm điều kiện so sánh với so_gio_dat_ve_truoc
        query += " TIMESTAMPDIFF(HOUR, NOW() ,lich_chuyen_bay.ngay_gio_khoi_hanh) >= (SELECT so_gio_dat_ve_truoc FROM quy_dinh)"
        cursor.execute(query, tuple(params))
        chuyen_bay_list = cursor.fetchall()
    quyen = session['user']['vai_tro'] or 'Khách hàng'
    return render_template('danh_sach_ban_ve.html', danh_sach_san_bay_di=danh_sach_san_bay_di,
                           danh_sach_san_bay_den=danh_sach_san_bay_den,
                           san_bay_di_selected=san_bay_di_selected, san_bay_den_selected=san_bay_den_selected,
                           ngay_khoi_hanh=ngay_khoi_hanh, chuyen_bay_list=chuyen_bay_list, quyen=quyen)


@ban_ve_routes.route('/ban_ve/<ma_ve>/<ma_lich_chuyen_bay>', methods=['GET', 'POST'])
def ban_ve(ma_ve, ma_lich_chuyen_bay):
    quyen = session['user']['vai_tro'] or 'Khách hàng'
    if request.method == 'GET':
        # Lấy thông tin chuyến bay
        query = """
            SELECT ve.*, chuyen_bay.*, lich_chuyen_bay.*, quy_dinh.*
            FROM ve_chuyen_bay AS ve
            JOIN chuyen_bay ON ve.ma_chuyen_bay = chuyen_bay.ma_chuyen_bay
            JOIN lich_chuyen_bay ON chuyen_bay.ma_chuyen_bay = lich_chuyen_bay.ma_chuyen_bay
            JOIN quy_dinh ON 1=1
            WHERE ve.ma_ve = %s
        """
        cursor.execute(query, (ma_ve,))
        result = cursor.fetchall()[0]
        print(result)
        if result:
            ve_chuyen_bay = result[:4]
            lich_chuyen_bay_info = result[7:13]

            quy_dinh_info = result[13:]

            # Kiểm tra còn ghế hay không
            so_gio_ban_ve_truoc = quy_dinh_info[-1]

            thoi_gian_ban_ve_truoc = lich_chuyen_bay_info[1] - timedelta(hours=so_gio_ban_ve_truoc)
            print(thoi_gian_ban_ve_truoc)
            if datetime.now() < thoi_gian_ban_ve_truoc:
                # Lấy thông tin số ghế hạng 1 và hạng 2
                so_ghe_hang_1 = lich_chuyen_bay_info[4]
                so_ghe_hang_2 = lich_chuyen_bay_info[5]

                # Tính số ghế đã đặt cho hạng 1 và hạng 2
                query_seats = """
                    SELECT COUNT(*) 
                    FROM dat_ve_chuyen_bay AS dat_ve
                    JOIN ve_chuyen_bay AS ve ON dat_ve.ma_ve = ve.ma_ve
                    WHERE dat_ve.ma_lich_chuyen_bay = %s
                    AND ve.hang_ve = %s
                """
                cursor.execute(query_seats, (ma_lich_chuyen_bay, 'Hạng 1'))
                booked_seats_hang_1 = cursor.fetchone()[0]

                cursor.execute(query_seats, (ma_lich_chuyen_bay, 'Hạng 2'))
                booked_seats_hang_2 = cursor.fetchone()[0]

                # Kiểm tra số ghế còn trống

                if ve_chuyen_bay[3] > 0 and booked_seats_hang_1 < so_ghe_hang_1 and booked_seats_hang_2 < so_ghe_hang_2:
                    return render_template('ban_ve.html', ve_chuyen_bay=ve_chuyen_bay,
                                           ma_lich_chuyen_bay=ma_lich_chuyen_bay, quyen=quyen)
                else:
                    flash('Không thể đặt vé cho chuyến bay này do hết chỗ.')
                    return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))

            else:
                flash('Không thể đặt vé cho chuyến bay này do đã quá thời gian đặt vé.')
                return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))

        flash('Không tìm thấy thông tin chuyến bay.')
        return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))


    elif request.method == 'POST':
        # Lấy thông tin từ form
        ma_ve_post = request.form['ma_ve']
        ma_lich_chuyen_bay = request.form['ma_lich_chuyen_bay']
        ho_ten = request.form['ho_ten']
        cmnd_cccd = request.form['cmnd_cccd']
        so_dien_thoai = request.form['so_dien_thoai']
        so_tien = request.form['so_tien']

        # Kiểm tra còn ghế hay không
        query = """
            SELECT ve.*, chuyen_bay.*, lich_chuyen_bay.*, quy_dinh.*
            FROM ve_chuyen_bay AS ve
            JOIN chuyen_bay ON ve.ma_chuyen_bay = chuyen_bay.ma_chuyen_bay
            JOIN lich_chuyen_bay ON chuyen_bay.ma_chuyen_bay = lich_chuyen_bay.ma_chuyen_bay
            JOIN quy_dinh ON 1=1
            WHERE ve.ma_ve = %s
        """
        cursor.execute(query, (ma_ve_post,))
        result = cursor.fetchall()[0]

        if result:
            ve_chuyen_bay = result[:4]
            lich_chuyen_bay_info = result[7:13]
            quy_dinh_info = result[13:]

            # Kiểm tra thời gian bán vé
            so_gio_ban_ve_truoc = quy_dinh_info[-1]
            thoi_gian_ban_ve_truoc = lich_chuyen_bay_info[1] - timedelta(hours=so_gio_ban_ve_truoc)

            if datetime.now() < thoi_gian_ban_ve_truoc:
                # Lấy thông tin số ghế hạng 1 và hạng 2
                so_ghe_hang_1 = lich_chuyen_bay_info[4]
                so_ghe_hang_2 = lich_chuyen_bay_info[5]

                # Tính số ghế đã đặt cho hạng 1 và hạng 2
                query_seats = """
                    SELECT COUNT(*) 
                    FROM dat_ve_chuyen_bay AS dat_ve
                    JOIN ve_chuyen_bay AS ve ON dat_ve.ma_ve = ve.ma_ve
                    WHERE dat_ve.ma_lich_chuyen_bay = %s
                    AND ve.hang_ve = %s
                """
                cursor.execute(query_seats, (ma_lich_chuyen_bay, 'Hạng 1'))
                booked_seats_hang_1 = cursor.fetchone()[0]

                cursor.execute(query_seats, (ma_lich_chuyen_bay, 'Hạng 2'))
                booked_seats_hang_2 = cursor.fetchone()[0]

                # Kiểm tra số ghế còn trống
                if ve_chuyen_bay[3] > 0 and booked_seats_hang_1 < so_ghe_hang_1 and booked_seats_hang_2 < so_ghe_hang_2:
                    # Thực hiện chèn dữ liệu vào bảng dat_ve_chuyen_bay và lấy mã đặt vé
                    cursor.execute(
                        "INSERT INTO dat_ve_chuyen_bay (ho_ten, cmnd_cccd, so_dien_thoai, ma_ve, ma_lich_chuyen_bay) VALUES (%s, %s, %s, %s, %s)",
                        (ho_ten, cmnd_cccd, so_dien_thoai, ma_ve_post, ma_lich_chuyen_bay))
                    db.commit()

                    # Lấy mã đặt vé vừa được chèn
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    ma_dat_ve = cursor.fetchone()[0]

                    # Thực hiện chèn dữ liệu vào bảng phuong_thuc_thanh_toan
                    cursor.execute(
                        "INSERT INTO thanh_toan (ma_dat_ve, pttt, trang_thai, so_tien) VALUES (%s, N'Tại quầy', N'Thành công', %s)",
                        (ma_dat_ve, so_tien))
                    db.commit()
                    flash('Bán vé và thanh toán thành công.')
                    return redirect(url_for('ban_ve_routes.thong_tin_ve', ma_dat_ve=ma_dat_ve))
                else:
                    flash('Không thể đặt vé cho chuyến bay này do hết chỗ.')
                    return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))
            else:
                flash('Không thể đặt vé cho chuyến bay này do đã quá thời gian bán vé.')
                return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))

        flash('Không tìm thấy thông tin chuyến bay.')
        return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))


@ban_ve_routes.route('/thong_tin_ve/<ma_dat_ve>', methods=['GET'])
def thong_tin_ve(ma_dat_ve):
    # Query to get information of the booked ticket
    query = """
        SELECT dat_ve.*, ve.*, chuyen_bay.*, lich_chuyen_bay.*
        FROM dat_ve_chuyen_bay AS dat_ve
        JOIN ve_chuyen_bay AS ve ON dat_ve.ma_ve = ve.ma_ve
        JOIN chuyen_bay ON ve.ma_chuyen_bay = chuyen_bay.ma_chuyen_bay
        JOIN lich_chuyen_bay ON chuyen_bay.ma_chuyen_bay = lich_chuyen_bay.ma_chuyen_bay
        WHERE dat_ve.ma_dat_ve = %s
    """
    cursor.execute(query, (ma_dat_ve,))
    result = cursor.fetchall()[0]

    if result:

        thong_tin_dat_ve = result[0:6]

        thong_tin_ve_chuyen_bay = result[8:12]
        thong_tin_chuyen_bay = result[12:]

        quyen = session['user']['vai_tro'] or 'Khách hàng'
        return render_template('thong_tin_ve.html', thong_tin_dat_ve=thong_tin_dat_ve,
                               thong_tin_ve_chuyen_bay=thong_tin_ve_chuyen_bay,
                               thong_tin_chuyen_bay=thong_tin_chuyen_bay, quyen=quyen)
    else:
        flash('Không tìm thấy thông tin đặt vé.')
        return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))
