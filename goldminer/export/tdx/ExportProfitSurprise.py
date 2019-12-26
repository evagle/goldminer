# coding: utf-8
from goldminer.common.logger import get_logger
from goldminer.storage.ProfitSurpriseDao import ProfitSurpriseDao


class ExportProfitSurprise:
    def __init__(self):
        self.profit_surprise_dao = ProfitSurpriseDao()
        self._logger = get_logger(__name__)

    def get_surprises(self):
        surprises = self.profit_surprise_dao.all()
        result = []
        for surprise in surprises:
            market = 1 if surprise.code[0:1] == "6" else 0
            result.append([str(market), surprise.code, surprise.trade_date.strftime("%Y%m%d"), "1"])

        return result

    def export(self, out_path):
        result = self.get_surprises()
        self.save_to_file(result, out_path)

    def save_to_file(self, data, out_path):
        with open(out_path, "w") as writer:
            lines = []
            for row in data:
                lines.append("|".join(row) + "\n")
            writer.writelines(lines)
            self._logger.info("Save {} surprises to {}".format(len(data), out_path))


if __name__ == "__main__":
    export_helper = ExportProfitSurprise()
    export_helper.export("/Users/abing/Downloads/ProfitSurprise.tdx.txt")
