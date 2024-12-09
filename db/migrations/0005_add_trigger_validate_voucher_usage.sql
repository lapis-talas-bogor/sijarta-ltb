CREATE OR REPLACE FUNCTION validate_voucher_usage()
RETURNS TRIGGER AS $$
DECLARE
    banyak_digunakan INT;
    kuota INT;
    expired_tgl DATE;
BEGIN
    -- Ambil data kuota penggunaan dan tanggal expired voucher
    SELECT NEW.telah_digunakan, kuota_penggunaan, NEW.tgl_awal + jml_hari_berlaku
    INTO banyak_digunakan, kuota, expired_tgl
    FROM SIJARTA.VOUCHER
    WHERE kode = NEW.id_voucher;

    -- Periksa apakah kuota penggunaan voucher telah habis
    IF banyak_digunakan IS NOT NULL AND banyak_digunakan > kuota THEN
        RAISE EXCEPTION 'Voucher % sudah mencapai batas jumlah penggunaan', NEW.id_voucher;
    END IF;

    -- Periksa apakah voucher telah melewati batas hari berlaku
    IF expired_tgl IS NOT NULL AND expired_tgl < CURRENT_DATE THEN
        RAISE EXCEPTION 'Voucher % sudah melewati batas hari berlaku', NEW.id_voucher;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER validate_voucher_trigger
BEFORE UPDATE ON SIJARTA.TR_PEMBELIAN_VOUCHER
FOR EACH ROW
EXECUTE FUNCTION validate_voucher_usage();
