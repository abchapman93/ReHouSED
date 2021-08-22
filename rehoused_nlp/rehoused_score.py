def calculate_rehoused(df,
                       window_size=30,
                       patient_col="pt_id",
                       time_col="time_to_index",
                       doc_class_col="document_classification"):
    """Calculate the NLP-derived ReHouSED score for a cohort of patients.
    Args:
        df (pandas.DataFrame): A DataFrame with at least the 3 columns corresponding to
            `patient_col`, `time_col`, and `doc_class_col`
        window_size (int): The size of fixed time windows over which to aggregate document classifications.
            Default 30
        patient_col (str): Column for patient identifiers over which to group by.
            Default 'pt_id'
        time_col (str): Column containing the number of days to the index date for each document.
            Default 'time_to_index'
        doc_class_col (str): Column containing NLP-derived document classifications.
            Default 'document_classification'
    Returns: DataFrame where each row corresponds to a single patient time interval
    """
    df = df[[patient_col, time_col, doc_class_col]]
    # Filter out unknown documents
    df = df[df[doc_class_col] != "UNKNOWN"]

    # First, group each document into a discrete time interval
    df["time_window"] = df[time_col] // window_size

    # Next, pivot to patient and time window
    rehoused = df.pivot_table(index=[patient_col, "time_window"], columns=[doc_class_col], aggfunc=len, fill_value=0)
    # Selected the single level
    rehoused = rehoused[time_col]

    rehoused["total_documents"] = rehoused["STABLY_HOUSED"] + rehoused["UNSTABLY_HOUSED"]
    rehoused["rehoused"] = rehoused["STABLY_HOUSED"] / rehoused["total_documents"]

    # Now flatten
    rehoused = rehoused.sort_values([patient_col, "time_window"]).reset_index()
    rehoused.columns = rehoused.columns.rename(None)

    return rehoused