import React, { useState } from 'react';
import { CapacityCalculation } from '../types';
import AdvisoryBadge from './AdvisoryBadge';

interface CapacityCalculatorProps {
  initialCapacity: CapacityCalculation;
  onRecalculate?: (params: {
    built_up_area_sqm: number;
    faculty_count: number;
    applied_intake: number;
  }) => Promise<CapacityCalculation>;
  className?: string;
}

export const CapacityCalculator: React.FC<CapacityCalculatorProps> = ({
  initialCapacity,
  onRecalculate,
  className = '',
}) => {
  const [capacity, setCapacity] = useState<CapacityCalculation>(initialCapacity);
  const [area, setArea] = useState(initialCapacity.built_up_area_sqm);
  const [faculty, setFaculty] = useState(initialCapacity.faculty_count);
  const [applied, setApplied] = useState(initialCapacity.applied_intake);
  const [isCalculating, setIsCalculating] = useState(false);

  const handleSimulate = async () => {
    if (!onRecalculate) return;
    setIsCalculating(true);
    try {
      const updated = await onRecalculate({
        built_up_area_sqm: area,
        faculty_count: faculty,
        applied_intake: applied,
      });
      setCapacity(updated);
    } catch {
      // offline fallback
      const maxInfra = Math.floor(area / 8.5);
      const maxFac = faculty * 20;
      const approved = Math.min(applied, maxInfra, maxFac);
      const bottleneck =
        maxInfra < maxFac ? 'infrastructure' : maxFac < maxInfra ? 'faculty' : 'balanced';

      setCapacity({
        built_up_area_sqm: area,
        required_sqm_per_student: 8.5,
        faculty_count: faculty,
        faculty_ratio_required: 20,
        max_capacity_infrastructure: maxInfra,
        max_capacity_faculty: maxFac,
        bottleneck_factor: bottleneck,
        applied_intake: applied,
        suggested_approved_intake: approved,
        explanation: `Calculated capacity dynamically: Infrastructure supports ${maxInfra} students, Faculty roster supports ${maxFac} students. Constraint factor: ${bottleneck.toUpperCase()}.`,
      });
    } finally {
      setIsCalculating(false);
    }
  };

  const maxScale = Math.max(
    capacity.applied_intake,
    capacity.max_capacity_infrastructure,
    capacity.max_capacity_faculty,
    600
  );

  return (
    <div className={`bg-white rounded-xl border border-slate-200 shadow-sm p-6 ${className}`}>
      <div className="flex items-center justify-between border-b border-slate-200 pb-4 mb-5">
        <div>
          <h3 className="text-base font-bold text-slate-800">
            Intake Capacity vs Infrastructure Calculator
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated dimensional ceiling check linking physical area and valid faculty roster
          </p>
        </div>
        <AdvisoryBadge />
      </div>

      {/* Visual Capacity Comparison Bars */}
      <div className="space-y-4 mb-6">
        {/* Applied Intake Bar */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="font-semibold text-slate-700">Applied Intake (Requested by College)</span>
            <span className="font-mono font-bold text-slate-900">{capacity.applied_intake} seats</span>
          </div>
          <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all duration-300"
              style={{ width: `${(capacity.applied_intake / maxScale) * 100}%` }}
            />
          </div>
        </div>

        {/* Infrastructure Ceiling */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="font-semibold text-slate-700">
              Infrastructure Ceiling (Based on {capacity.built_up_area_sqm} sq.m instructional area @ 8.5 m²/student)
            </span>
            <span className="font-mono font-bold text-slate-900">
              {capacity.max_capacity_infrastructure} seats
            </span>
          </div>
          <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-300"
              style={{ width: `${(capacity.max_capacity_infrastructure / maxScale) * 100}%` }}
            />
          </div>
        </div>

        {/* Faculty Roster Ceiling */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="font-semibold text-slate-700">
              Faculty Ceiling (Based on {capacity.faculty_count} verified faculty @ teacher-student norm [Reference - verify against Approval Process Handbook] (illustrative))
            </span>
            <span className="font-mono font-bold text-slate-900">
              {capacity.max_capacity_faculty} seats
            </span>
          </div>
          <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-amber-500 rounded-full transition-all duration-300"
              style={{ width: `${(capacity.max_capacity_faculty / maxScale) * 100}%` }}
            />
          </div>
        </div>

        {/* Suggested Approved Intake Ceiling */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="font-bold text-emerald-800">
              Suggested Approved Intake (Constrained by bottleneck)
            </span>
            <span className="font-mono font-extrabold text-emerald-700 text-sm">
              {capacity.suggested_approved_intake} seats
            </span>
          </div>
          <div className="h-3.5 w-full bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-600 rounded-full transition-all duration-300 shadow-sm"
              style={{ width: `${(capacity.suggested_approved_intake / maxScale) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Bottleneck Callout */}
      <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between text-xs mb-6">
        <div className="flex items-center gap-2">
          <span className="text-slate-500">Identified Bottleneck:</span>
          <span className="font-bold uppercase px-2 py-0.5 rounded bg-rose-100 text-rose-800 border border-rose-300">
            {capacity.bottleneck_factor} Constraint
          </span>
        </div>
        <p className="text-slate-600 text-[11px] max-w-md italic">{capacity.explanation}</p>
      </div>

      {/* Interactive Simulation Controls */}
      <div className="bg-slate-50/70 p-4 rounded-lg border border-slate-200">
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
          Simulate Parameter Adjustments (What-If Analysis)
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Instructional Area (sq.m)
            </label>
            <input
              type="number"
              value={area}
              onChange={(e) => setArea(Number(e.target.value))}
              className="w-full text-xs p-2 border border-slate-300 rounded focus:ring-1 focus:ring-aicte-500 bg-white"
            />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Verified Faculty Count
            </label>
            <input
              type="number"
              value={faculty}
              onChange={(e) => setFaculty(Number(e.target.value))}
              className="w-full text-xs p-2 border border-slate-300 rounded focus:ring-1 focus:ring-aicte-500 bg-white"
            />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Applied Intake Request
            </label>
            <input
              type="number"
              value={applied}
              onChange={(e) => setApplied(Number(e.target.value))}
              className="w-full text-xs p-2 border border-slate-300 rounded focus:ring-1 focus:ring-aicte-500 bg-white"
            />
          </div>
        </div>

        <div className="mt-3 flex justify-end">
          <button
            type="button"
            onClick={handleSimulate}
            disabled={isCalculating}
            className="px-4 py-2 bg-aicte-600 hover:bg-aicte-700 text-white rounded text-xs font-semibold shadow-sm transition"
          >
            {isCalculating ? 'Recalculating...' : 'Re-calculate Ceiling'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CapacityCalculator;
