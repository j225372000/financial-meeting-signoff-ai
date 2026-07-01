if st.button("開始執行", type="primary"):

    with st.spinner("執行中，請稍候..."):

        # Morning 改用 Pipeline
        if job == "每日金融晨報":

            result = run_morning_pipeline()

            st.success("Morning Pipeline 執行完成")

            st.write(result)

        # 其它仍使用 subprocess
        else:

            result = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )

            st.subheader("執行結果")
            st.text(result.stdout)

            if result.stderr:
                st.subheader("系統訊息")
                st.warning(result.stderr)

    if Path(output_file).exists():

        st.success("已產生輸出檔案")

        with open(output_file, "rb") as f:

            st.download_button(
                label="下載結果",
                data=f,
                file_name=Path(output_file).name
            )

    else:

        st.warning("尚未找到輸出檔案")
