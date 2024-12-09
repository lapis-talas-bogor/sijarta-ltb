CREATE OR REPLACE FUNCTION validate_voucher_usage()
RETURNS TRIGGER AS $$
DECLARE
    telah_digunakan INT;
    kuota_penggunaan INT;
    tgl_expired DATE;
BEGIN
    -- Ambil data kuota penggunaan dan tanggal expired voucher
    SELECT NEW.telah_digunakan, kuota_penggunaan, NEW.tgl_awal + jml_hari_berlaku
    INTO telah_digunakan, kuota_penggunaan, tgl_expired
    FROM SIJARTA.VOUCHER
    WHERE kode = NEW.id_voucher;

    -- Periksa apakah kuota penggunaan voucher telah habis
    IF telah_digunakan IS NOT NULL AND telah_digunakan > kuota_penggunaan THEN
        RAISE EXCEPTION 'Voucher % sudah mencapai batas jumlah penggunaan', NEW.id_voucher;
    END IF;

    -- Periksa apakah voucher telah melewati batas hari berlaku
    IF tgl_expired IS NOT NULL AND tgl_expired < CURRENT_DATE THEN
        RAISE EXCEPTION 'Voucher % sudah melewati batas hari berlaku', NEW.id_voucher;
    END IF;

    -- Jika semua validasi lolos, kurangi kuota penggunaan voucher
    UPDATE SIJARTA.TR_PEMBELIAN_VOUCHER
    SET telah_digunakan = telah_digunakan + 1
    WHERE kode = NEW.id_voucher;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER validate_voucher_trigger
BEFORE INSERT OR UPDATE ON SIJARTA.TR_PEMBELIAN_VOUCHER
FOR EACH ROW
EXECUTE FUNCTION validate_voucher_usage();
