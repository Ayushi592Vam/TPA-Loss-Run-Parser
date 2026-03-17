"""
ui/topbar.py
Renders the top navigation bar: logo, title, schema badge, settings gear.
Returns True if the settings dialog should be opened.
"""

import streamlit as st
from modules.logo import logo_img_tag


def _navbar_badge_html(active_schema: str | None, schemas: dict) -> str:
    if not active_schema or active_schema not in schemas:
        return ""
    sc = schemas[active_schema]
    return (
        f'<span style="'
        f'display:inline-flex;align-items:center;gap:6px;'
        f'border-radius:6px;padding:4px 14px;'
        f'font-size:12px;font-weight:700;font-family:monospace;'
        f'border:1px solid {sc["color"]}55;'
        f'color:{sc["color"]};background:{sc["color"]}12;'
        f'white-space:nowrap;letter-spacing:0.3px;margin-left:20px;">'
        f'{sc["icon"]} {active_schema} &nbsp;&middot;&nbsp; {sc["version"]}</span>'
    )


def render_topbar(schemas: dict, config_load_status: dict) -> bool:
    """
    Renders the top bar.
    Returns True if the settings gear was clicked (caller should open dialog).
    """
    active_schema = st.session_state.get("active_schema", None)
    _logo         = logo_img_tag(height=52)
    _badge        = _navbar_badge_html(active_schema, schemas)

    col_title, col_gear = st.columns([11, 1])

    with col_title:
        st.markdown(
            '<div style="'
            'display:flex;align-items:center;'
            'padding:10px 0 8px 0;min-height:60px;'
            '">'

            # Logo — rendered exactly as source, no clipping
            + _logo +

            # Title + subtitle block
            '<div style="'
            'display:flex;flex-direction:column;'
            'justify-content:center;gap:3px;'
            '">'

            # App title
            '<span style="'
            'font-size:17px;font-weight:700;color:#ffffff;'
            'font-family:\'Segoe UI\',\'Helvetica Neue\',Arial,sans-serif;'
            'letter-spacing:-0.3px;line-height:1.2;white-space:nowrap;'
            '">&#128737;&nbsp; TPA Loss Run Parser</span>'

            # Professional subtitle
            '<span style="'
            'font-size:11px;font-weight:400;color:#8888bb;'
            'font-family:\'JetBrains Mono\',\'Cascadia Code\',\'Consolas\',monospace;'
            'letter-spacing:0.4px;white-space:nowrap;'
            '">Automated Claims Data Ingestion &amp; Multi-Schema Export Platform</span>'

            '</div>'

            # Schema badge (if active)
            + (_badge if _badge else '') +

            '</div>',
            unsafe_allow_html=True,
        )

    with col_gear:
        st.markdown("<div style='padding-top:16px;'>", unsafe_allow_html=True)
        clicked = st.button("⚙", key="open_settings", help="Settings", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<hr style="border:none;border-top:1px solid #2a2a45;margin:2px 0 18px 0;">',
        unsafe_allow_html=True,
    )
    return clicked
