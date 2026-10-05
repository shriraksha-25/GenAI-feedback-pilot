import React, { useEffect, useState } from 'react';
import { planningService } from '../services/planningService';
import { insightsService } from '../services/insightsService';

import StatusBadge from '../components/common/StatusBadge';
import Button from '../components/common/Button';
import EmptyState from '../components/common/EmptyState';
import ErrorState from '../components/common/ErrorState';
import { TableSkeleton } from '../components/common/LoadingState';
import Modal from '../components/common/Modal';

import {
  FileText,
  Sparkles,
  RefreshCw,
  BookOpen,
  CheckSquare,
} from 'lucide-react';

export default function Requirements() {
  const [features, setFeatures] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] =
    useState(false);
  const [error, setError] = useState(null);

  const [selectedFeature, setSelectedFeature] =
    useState(null);

  const [selectedPRD, setSelectedPRD] =
    useState(null);

  const [generatedStories, setGeneratedStories] =
    useState([]);

  const loadFeatures = async () => {
    setIsLoading(true);
    setError(null);

    try {
      let data =
        await planningService.getFeatures();

      if (data.length === 0) {
        const insights =
          await insightsService.getInsights();

        const opportunities =
          insights.priorityOpportunities || [];

        for (const opportunity of opportunities) {
          if (!opportunity.title) {
            continue;
          }

          try {
            await planningService.createFeature({
              title: opportunity.title,
              description:
                opportunity.description || '',
              theme:
                opportunity.theme || null,
              pain_point:
                opportunity.pain_point || null,
              feature_category:
                opportunity.feature_category ||
                opportunity.recommendedAction ||
                null,
              source_feedback_ids:
                opportunity.source_feedback_ids ||
                [],
              created_by: 'frontend',
            });
          } catch (createError) {
            console.warn(
              `Unable to create feature "${opportunity.title}"`,
              createError
            );
          }
        }

        data =
          await planningService.getFeatures();
      }

      setFeatures(data);
    } catch (err) {
      console.error(
        'Requirements load error:',
        err
      );

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          'Unable to load feature opportunities.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFeatures();
  }, []);

  const handleGeneratePRD = async (feature) => {
    setIsGenerating(true);
    setError(null);
    setGeneratedStories([]);

    try {
      const prd =
        await planningService.generatePRD(
          feature.feature_id
        );

      setSelectedFeature(feature);
      setSelectedPRD(prd);
    } catch (err) {
      console.error(
        'PRD generation error:',
        err
      );

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          'Failed to generate PRD.'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateStories = async () => {
    if (
      !selectedFeature ||
      !selectedPRD
    ) {
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      /*
       * The API response contains the newly generated
       * user stories. Keep that response directly in
       * the UI instead of expecting the PRD endpoint
       * to contain the stories.
       */
      const result =
        await planningService.generateUserStories(
          selectedFeature.feature_id,
          selectedPRD.prd_id
        );

      console.log(
        'Generated user stories:',
        result
      );

      /*
       * Support the possible response shapes:
       *
       * [...]
       * { user_stories: [...] }
       * { stories: [...] }
       * { items: [...] }
       */
      let stories = [];

      if (Array.isArray(result)) {
        stories = result;
      } else if (
        Array.isArray(result?.user_stories)
      ) {
        stories = result.user_stories;
      } else if (
        Array.isArray(result?.stories)
      ) {
        stories = result.stories;
      } else if (
        Array.isArray(result?.items)
      ) {
        stories = result.items;
      }

      setGeneratedStories(stories);

      /*
       * Refresh feature status so the table changes
       * to stories_generated.
       */
      const refreshedFeatures =
        await planningService.getFeatures();

      setFeatures(refreshedFeatures);
    } catch (err) {
      console.error(
        'User story generation error:',
        err
      );

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          'Failed to generate user stories.'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const closePRDModal = () => {
    setSelectedPRD(null);
    setSelectedFeature(null);
    setGeneratedStories([]);
  };

  const renderValue = (value) => {
    if (
      value === null ||
      value === undefined
    ) {
      return '';
    }

    if (
      typeof value === 'string' ||
      typeof value === 'number' ||
      typeof value === 'boolean'
    ) {
      return String(value);
    }

    try {
      return JSON.stringify(
        value,
        null,
        2
      );
    } catch {
      return String(value);
    }
  };

  const getStoryTitle = (
    story,
    index
  ) => {
    if (
      typeof story === 'string'
    ) {
      return story;
    }

    return (
      story?.title ||
      story?.name ||
      story?.user_story ||
      `User Story ${index + 1}`
    );
  };

  const getStoryDescription = (
    story
  ) => {
    if (
      !story ||
      typeof story === 'string'
    ) {
      return null;
    }

    return (
      story.description ||
      story.story ||
      story.acceptance_criteria ||
      story.details ||
      null
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200/60 gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Requirements Management
          </h1>

          <p className="text-sm text-slate-500 mt-0.5">
            Convert prioritized feature
            opportunities into PRDs and user
            stories.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={loadFeatures}
          icon={RefreshCw}
          disabled={isLoading}
        >
          Refresh
        </Button>
      </div>

      {/* Error */}
      {error && (
        <ErrorState
          title="Requirements Service Alert"
          message={error}
          onRetry={loadFeatures}
        />
      )}

      {/* Features */}
      {isLoading ? (
        <TableSkeleton
          rows={5}
          cols={5}
        />
      ) : features.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No feature opportunities available"
          description="Analyze customer feedback first to identify feature opportunities."
        />
      ) : (
        <div className="bg-white rounded-lg border border-slate-200 shadow-subtle overflow-hidden">
          <div className="p-5 border-b border-slate-200">
            <h2 className="text-sm font-semibold text-slate-900">
              Feature Opportunities
            </h2>

            <p className="text-xs text-slate-500 mt-1">
              AI-generated opportunities from
              customer feedback. Generate a PRD
              and then create user stories.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3">
                    Feature
                  </th>

                  <th className="px-4 py-3">
                    Theme
                  </th>

                  <th className="px-4 py-3">
                    Category
                  </th>

                  <th className="px-4 py-3">
                    Status
                  </th>

                  <th className="px-4 py-3 text-right">
                    Action
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100 text-xs">
                {features.map(
                  (feature) => (
                    <tr
                      key={
                        feature.feature_id
                      }
                      className="hover:bg-slate-50/60"
                    >
                      <td className="px-5 py-4">
                        <div className="font-semibold text-slate-900">
                          {feature.title ||
                            'Untitled Feature'}
                        </div>

                        {feature.description && (
                          <div className="text-[11px] text-slate-500 mt-1 max-w-md">
                            {
                              feature.description
                            }
                          </div>
                        )}
                      </td>

                      <td className="px-4 py-4 text-slate-600">
                        {feature.theme ||
                          '—'}
                      </td>

                      <td className="px-4 py-4 text-slate-600">
                        {feature.feature_category ||
                          '—'}
                      </td>

                      <td className="px-4 py-4">
                        <StatusBadge
                          status={
                            feature.status ||
                            'identified'
                          }
                        />
                      </td>

                      <td className="px-4 py-4 text-right">
                        <Button
                          variant="ai"
                          size="sm"
                          icon={Sparkles}
                          onClick={() =>
                            handleGeneratePRD(
                              feature
                            )
                          }
                          disabled={
                            isGenerating
                          }
                          isLoading={
                            isGenerating &&
                            selectedFeature?.feature_id ===
                              feature.feature_id
                          }
                          loadingText="Generating..."
                        >
                          Generate PRD
                        </Button>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* PRD + Stories Modal */}
      {selectedFeature &&
        selectedPRD && (
          <Modal
            isOpen={Boolean(
              selectedPRD
            )}
            onClose={
              closePRDModal
            }
            title={
              typeof selectedPRD.title ===
              'string'
                ? selectedPRD.title
                : 'Generated Product Requirements Document'
            }
            subtitle={`Feature: ${selectedFeature.title}`}
            footer={
              <div className="flex items-center justify-end gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={
                    closePRDModal
                  }
                >
                  Close
                </Button>

                <Button
                  variant="primary"
                  size="sm"
                  icon={BookOpen}
                  onClick={
                    handleGenerateStories
                  }
                  disabled={
                    isGenerating
                  }
                  isLoading={
                    isGenerating
                  }
                  loadingText="Generating Stories..."
                >
                  Generate User Stories
                </Button>
              </div>
            }
          >
            <div className="space-y-5 text-xs">
              {/* PRD */}
              <div>
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px]">
                  Product Requirement
                  Document
                </span>

                <div className="mt-2 p-4 rounded-lg bg-slate-50 border border-slate-200 whitespace-pre-wrap text-slate-800 leading-relaxed overflow-auto max-h-[400px]">
                  {renderValue(
                    selectedPRD.content
                  )}
                </div>
              </div>

              {/* PRD ID + Status */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3 rounded-lg border border-slate-200 bg-white">
                  <div className="text-[10px] uppercase tracking-wider text-slate-400">
                    PRD ID
                  </div>

                  <div className="mt-1 font-medium text-slate-700 break-all">
                    {selectedPRD.prd_id ||
                      '—'}
                  </div>
                </div>

                <div className="p-3 rounded-lg border border-slate-200 bg-white">
                  <div className="text-[10px] uppercase tracking-wider text-slate-400">
                    Status
                  </div>

                  <div className="mt-1">
                    <StatusBadge
                      status={
                        selectedPRD.status ||
                        'draft'
                      }
                    />
                  </div>
                </div>
              </div>

              {/* Generated User Stories */}
              {generatedStories.length >
                0 && (
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px]">
                      Generated User
                      Stories
                    </span>

                    <span className="text-[11px] text-slate-400">
                      {
                        generatedStories.length
                      }{' '}
                      stories
                    </span>
                  </div>

                  <div className="mt-2 space-y-3">
                    {generatedStories.map(
                      (
                        story,
                        index
                      ) => {
                        const title =
                          getStoryTitle(
                            story,
                            index
                          );

                        const description =
                          getStoryDescription(
                            story
                          );

                        return (
                          <div
                            key={
                              story?.user_story_id ||
                              story?.id ||
                              index
                            }
                            className="p-4 rounded-lg bg-white border border-slate-200"
                          >
                            <div className="flex items-start gap-3">
                              <CheckSquare className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />

                              <div className="min-w-0 flex-1">
                                <div className="font-semibold text-slate-800">
                                  {title}
                                </div>

                                {description && (
                                  <div className="text-slate-600 mt-2 leading-relaxed whitespace-pre-wrap">
                                    {renderValue(
                                      description
                                    )}
                                  </div>
                                )}

                                {story?.acceptance_criteria &&
                                  description !==
                                    story.acceptance_criteria && (
                                    <div className="mt-3">
                                      <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
                                        Acceptance Criteria
                                      </div>

                                      <div className="mt-1 text-slate-600 whitespace-pre-wrap">
                                        {renderValue(
                                          story.acceptance_criteria
                                        )}
                                      </div>
                                    </div>
                                  )}
                              </div>
                            </div>
                          </div>
                        );
                      }
                    )}
                  </div>
                </div>
              )}

              {/* No stories returned */}
              {generatedStories.length ===
                0 && (
                <div className="p-4 rounded-lg border border-dashed border-slate-300 text-center">
                  <BookOpen className="w-5 h-5 mx-auto text-slate-400" />

                  <p className="text-xs text-slate-500 mt-2">
                    User stories have been
                    generated and the feature
                    status is updated.
                  </p>

                  <p className="text-[11px] text-slate-400 mt-1">
                    No story objects were
                    returned by the API response
                    to display in this modal.
                  </p>
                </div>
              )}
            </div>
          </Modal>
        )}
    </div>
  );
}