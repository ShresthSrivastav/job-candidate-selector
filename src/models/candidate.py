from __future__ import annotations
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class CareerItem(BaseModel):
    company: Optional[str]
    title: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    duration_months: Optional[int]
    is_current: Optional[bool]
    industry: Optional[str]
    company_size: Optional[str]
    description: Optional[str]


class SkillItem(BaseModel):
    name: Optional[str]
    proficiency: Optional[str]
    endorsements: Optional[int]
    duration_months: Optional[int]


class EducationItem(BaseModel):
    institution: Optional[str]
    degree: Optional[str]
    field_of_study: Optional[str]
    start_year: Optional[int]
    end_year: Optional[int]
    grade: Optional[str]
    tier: Optional[str]


class Profile(BaseModel):
    anonymized_name: Optional[str]
    headline: Optional[str]
    summary: Optional[str]
    location: Optional[str]
    country: Optional[str]
    years_of_experience: Optional[float]
    current_title: Optional[str]
    current_company: Optional[str]
    current_company_size: Optional[str]
    current_industry: Optional[str]


class RedrobSignals(BaseModel):
    profile_completeness_score: Optional[float]
    signup_date: Optional[str]
    last_active_date: Optional[str]
    open_to_work_flag: Optional[bool]
    profile_views_received_30d: Optional[int]
    applications_submitted_30d: Optional[int]
    recruiter_response_rate: Optional[float]
    avg_response_time_hours: Optional[float]
    # Keep flexible additional properties
    skill_assessment_scores: Optional[dict] = Field(default_factory=dict)
    connection_count: Optional[int]
    endorsements_received: Optional[int]
    notice_period_days: Optional[int]
    expected_salary_range_inr_lpa: Optional[dict]
    preferred_work_mode: Optional[str]
    willing_to_relocate: Optional[bool]
    github_activity_score: Optional[float]
    search_appearance_30d: Optional[int]
    saved_by_recruiters_30d: Optional[int]
    interview_completion_rate: Optional[float]
    offer_acceptance_rate: Optional[float]
    verified_email: Optional[bool]
    verified_phone: Optional[bool]
    linkedin_connected: Optional[bool]


class Candidate(BaseModel):
    candidate_id: str
    profile: Optional[Profile]
    career_history: Optional[List[CareerItem]] = Field(default_factory=list)
    education: Optional[List[EducationItem]] = Field(default_factory=list)
    skills: Optional[List[SkillItem]] = Field(default_factory=list)
    certifications: Optional[List[dict]] = Field(default_factory=list)
    languages: Optional[List[dict]] = Field(default_factory=list)
    redrob_signals: Optional[RedrobSignals]
