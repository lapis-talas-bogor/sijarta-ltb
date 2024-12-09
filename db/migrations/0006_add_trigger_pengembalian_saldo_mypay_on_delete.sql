CREATE OR REPLACE FUNCTION pengembalian_saldo_mypay_on_delete()
RETURNS TRIGGER AS $$
DECLARE
    nominal_biaya DECIMAL(15, 2);
    id_pelanggan UUID;
BEGIN
    SELECT total_biaya, id_pelanggan
    INTO nominal_biaya, id_pelanggan
    FROM SIJARTA.TR_PEMESANAN_JASA
    WHERE id = OLD.id;

    UPDATE SIJARTA.USER
    SET saldo_mypay = saldo_mypay + nominal_biaya
    WHERE id = id_pelanggan;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER pengembalian_saldo_mypay_trigger_delete
AFTER DELETE
ON SIJARTA.TR_PEMESANAN_JASA
FOR EACH ROW
EXECUTE FUNCTION pengembalian_saldo_mypay_on_delete();
