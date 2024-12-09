CREATE OR REPLACE FUNCTION selesai_pesanan()
RETURNS TRIGGER AS $$
DECLARE pelanggan UUID;
DECLARE pekerja UUID;
DECLARE biaya DECIMAL;
BEGIN
    SELECT PJ.id_pelanggan INTO pelanggan FROM sijarta.TR_PEMESANAN_STATUS PS
    JOIN sijarta.TR_PEMESANAN_JASA PJ ON (PS.id_tr_pemesanan = PJ.id) 
    WHERE PS.id_tr_pemesanan = NEW.id_tr_pemesanan;

    SELECT PJ.id_pekerja INTO pekerja FROM sijarta.TR_PEMESANAN_STATUS PS
    JOIN sijarta.TR_PEMESANAN_JASA PJ ON (PS.id_tr_pemesanan = PJ.id) 
    WHERE PS.id_tr_pemesanan = NEW.id_tr_pemesanan;

    SELECT PJ.total_biaya INTO biaya FROM sijarta.TR_PEMESANAN_STATUS PS
    JOIN sijarta.TR_PEMESANAN_JASA PJ ON (PS.id_tr_pemesanan = PJ.id) 
    WHERE PS.id_tr_pemesanan = NEW.id_tr_pemesanan;

    IF NEW.Id_status = 'f33e4567-e89b-12d3-a456-426614174004' THEN
        UPDATE SIJARTA.USER SET saldo_mypay = saldo_mypay + biaya
        WHERE id = pekerja;

        INSERT INTO sijarta.TR_MYPAY VALUES
        (gen_random_uuid(), pekerja, NOW(), biaya, 'f23e4567-e89b-12d3-a456-426614174005');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_selesai_pesanan
AFTER UPDATE ON sijarta.TR_PEMESANAN_STATUS
FOR EACH ROW
EXECUTE FUNCTION selesai_pesanan(); 
