"""
ui/field_row.py
Reusable helper that renders a single editable field row
(label | confidence | original | modified | eye | edit | history | checkbox).
Used by both schema mode and plain mode in the claim panel.
"""

import streamlit as st

from modules.audit import _append_audit
from modules.field_history import _record_field_history

import datetime


def _conf_colors(conf: int, use_conf: bool, conf_thresh: int) -> tuple[str, str, str]:
    """Returns (conf_color, row_border, row_bg)."""
    if not use_conf:
        return "var(--t3)", "var(--b0)", "var(--bg)"
    if conf < conf_thresh:
        return "var(--red)", "rgba(248,113,113,0.3)", "var(--red-g)"
    if conf < 75:
        return "var(--yellow)", "rgba(245,200,66,0.3)", "var(--yellow-g)"
    if conf < 88:
        return "var(--yellow)", "var(--b0)", "var(--bg)"
    return "var(--green)", "var(--b0)", "var(--bg)"


def render_field_row(
    *,
    # identity
    schema_field: str,
    info: dict,
    # state keys
    mk: str,          # mod key
    ek: str,          # edit key
    xk: str,          # checkbox key
    # display flags
    is_req: bool,
    conf: int,
    excel_f: str,
    is_title_sourced: bool,
    # context
    selected_sheet: str,
    curr_claim_id: str,
    active: dict,
    excel_path: str,
    uploaded_name: str,
    active_schema: str | None,
    use_conf: bool,
    conf_thresh: int,
    # dialog callbacks (callables)
    open_eye_popup,
) -> None:
    conf_col, row_border, row_bg = _conf_colors(conf, use_conf, conf_thresh)
    # Initialise state
    if ek not in st.session_state:
        st.session_state[ek] = False
    if xk not in st.session_state:
        st.session_state[xk] = True
    if mk not in st.session_state:
        # Always initialise from raw extracted value — Modified == Extracted on load
        # Only diverges once the user explicitly edits the field
        st.session_state[mk] = info.get("value", "")

    _cur_val = st.session_state.get(mk, info.get("value", ""))
    _edited  = _cur_val != info.get("value", "")
    _dot     = "<span style='color:var(--yellow);font-size:8px;'>●</span> " if _edited else ""

    # Badges
    _badge_html = (
        "<span class='mandatory-asterisk' title='Mandatory'>*</span>"
        if is_req
        else "<span class='optional-badge'>OPT</span>"
    )

    _ink              = "var(--t0)" if is_req else "var(--t1)"
    _field_label_html = (
        f"<div style='min-height:40px;display:flex;flex-direction:column;justify-content:center;"
        f"color:{_ink};font-size:var(--sz-body);font-weight:600;text-transform:uppercase;"
        f"letter-spacing:0.8px;font-family:var(--font-head);'>"
        f"<div style='display:flex;align-items:center;gap:3px;flex-wrap:wrap;line-height:1.6;'>"
        f"{_dot}{schema_field}{_badge_html}</div></div>"
    )
    _conf_html = (
        f"<div style='min-height:40px;display:flex;flex-direction:column;justify-content:center;gap:4px;'>"
        f"<span style='background:{conf_col}20;border:1px solid {conf_col};border-radius:20px;"
        f"padding:2px 10px;font-size:var(--sz-body);color:{conf_col};font-weight:600;"
        f"font-family:var(--mono);'>{conf}%</span>"
        f"<div style='background:var(--s1);border-radius:4px;height:4px;width:80%;'>"
        f"<div style='background:{conf_col};height:4px;border-radius:4px;width:{conf}%;'>"
        f"</div></div></div>"
    )

    # Row border accent
    st.markdown(
        f"<div style='border-left:2px solid {row_border};background:{row_bg};"
        f"border-radius:0 4px 4px 0;padding:2px 0 2px 4px;margin:1px 0;'></div>",
        unsafe_allow_html=True,
    )

    def _edit_col():
        _display_val = st.session_state.get(mk, info.get("value", "")) or ""
        if st.session_state[ek]:
            with st.form(
                key=f"form_s_{selected_sheet}_{curr_claim_id}_{schema_field}", border=False
            ):
                nv        = st.text_input("m", value=_display_val, label_visibility="collapsed")
                submitted = st.form_submit_button("", use_container_width=False)
                if submitted:
                    old_val = _display_val
                    st.session_state[mk] = nv
                    if (
                        not is_title_sourced
                        and excel_f in active["data"][st.session_state.selected_idx]
                    ):
                        active["data"][st.session_state.selected_idx][excel_f]["modified"] = nv
                    st.session_state[ek] = False
                    _record_field_history(selected_sheet, curr_claim_id, schema_field, old_val, nv)
                    _append_audit({
                        "event":     "FIELD_EDITED",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "filename":  uploaded_name,
                        "sheet":     selected_sheet,
                        "claim_id":  curr_claim_id,
                        "field":     schema_field,
                        "original":  info["value"],
                        "new_value": nv,
                    })
                    st.rerun()
        else:
            st.text_input(
                "m", value=_display_val,
                key=f"disp_{mk}", label_visibility="collapsed", disabled=True,
            )
        if (
            not is_title_sourced
            and excel_f in active["data"][st.session_state.selected_idx]
        ):
            active["data"][st.session_state.selected_idx][excel_f]["modified"] = (
                st.session_state.get(mk, info.get("value", "")) or ""
            )

    def _edit_btn():
        if not st.session_state[ek]:
            if st.button(
                "✏",
                key=f"ed_s_{selected_sheet}_{curr_claim_id}_{schema_field}",
                use_container_width=True,
                help="Edit field",
            ):
                st.session_state[ek] = True
                st.rerun()
        else:
            st.markdown(
                "<div style='height:38px;display:flex;align-items:center;justify-content:center;"
                "color:var(--green);font-size:11px;border:1px solid var(--b0);border-radius:6px;'>↵</div>",
                unsafe_allow_html=True,
            )

    if use_conf:
        cl, cc, co, cm, ce, cb, cx = st.columns(
            [1.8, 1.4, 1.6, 1.8, 0.45, 0.45, 0.40], gap="small"
        )
        with cl: st.markdown(_field_label_html, unsafe_allow_html=True)
        with cc: st.markdown(_conf_html, unsafe_allow_html=True)
        with co:
            st.text_input(
                "o", value=info["value"],
                key=f"orig_{selected_sheet}_{curr_claim_id}_schema_{schema_field}",
                label_visibility="collapsed", disabled=True,
            )
        with cm: _edit_col()
        with ce:
            if st.button(
                "👁",
                key=f"eye_s_{selected_sheet}_{curr_claim_id}_{schema_field}",
                use_container_width=True,
            ):
                open_eye_popup(schema_field, info, excel_path, selected_sheet)
        with cb: _edit_btn()
        with cx:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            st.checkbox("", key=xk, label_visibility="collapsed")
    else:
        cl, co, cm, ce, cb, cx = st.columns(
            [1.8, 1.8, 1.8, 0.45, 0.45, 0.40], gap="small"
        )
        with cl: st.markdown(_field_label_html, unsafe_allow_html=True)
        with co:
            st.text_input(
                "o", value=info["value"],
                key=f"orig_{selected_sheet}_{curr_claim_id}_schema_{schema_field}",
                label_visibility="collapsed", disabled=True,
            )
        with cm: _edit_col()
        with ce:
            if st.button(
                "👁",
                key=f"eye_s_{selected_sheet}_{curr_claim_id}_{schema_field}",
                use_container_width=True,
            ):
                open_eye_popup(schema_field, info, excel_path, selected_sheet)
        with cb: _edit_btn()
        with cx:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            st.checkbox("", key=xk, label_visibility="collapsed")
