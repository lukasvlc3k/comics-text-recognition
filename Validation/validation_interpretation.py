import os.path


def get_results_from_file(file):
    with open(file, "r") as f:
        f1_line = f.readline()
        jac_line = f.readline()
        tp_line = f.readline()
        fp_line = f.readline()
        fn_line = f.readline()
        wer_line = f.readline()
        cer_line = f.readline()
        ed_line = f.readline()
        wer_w_line = f.readline()
        cer_w_line = f.readline()
        ed_w_line = f.readline()

        f1 = float(f1_line.split(" = ")[1].strip())
        jaccard = float(jac_line.split(" = ")[1].strip())

        tp = int(tp_line.split(" = ")[1].strip())
        fp = int(fp_line.split(" = ")[1].strip())
        fn = int(fn_line.split(" = ")[1].strip())

        wer = float(wer_line.split(" = ")[1].strip())
        cer = float(cer_line.split(" = ")[1].strip())
        ed = float(ed_line.split(" = ")[1].strip())

        wer_w = float(wer_w_line.split(" = ")[1].strip())
        cer_w = float(cer_w_line.split(" = ")[1].strip())
        ed_w = float(ed_w_line.split(" = ")[1].strip())

        return f1, jaccard, tp, fp, fn, wer, cer, ed, wer_w, cer_w, ed_w


def print_results(results):
    for key in results:
        print(key, results[key])


def results_to_csv(results_base_dir, csv_path):
    with open(csv_path, "w") as f_stats:
        with os.scandir(results_base_dir) as entries:
            for entry in entries:
                name = entry.name
                result_file = entry.path + "/" + "validation.txt"
                if not os.path.isfile(result_file):
                    continue

                f1, jaccard, tp, fp, fn, wer, cer, ed, wer_w, cer_w, ed_w = get_results_from_file(result_file)

                if wer == -1:
                    continue

                line = name + ";" + str(f1) + ";" + str(jaccard) + ";" + str(tp) + ";" + str(fp) + ";" + str(
                    fn) + ";" + str(wer) + ";" + str(cer) + ";" + str(ed) + ";" + str(wer_w) + ";" + str(
                    cer_w) + ";" + str(
                    ed_w) + "\n"
                f_stats.write(line)
